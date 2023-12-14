import json
import csv
import tempfile
import zipfile
from collections import defaultdict

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.utils.text import slugify
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.views import View

from .models import ForecastModel
from .algos import LSTM, create_datasets


def download_forecast_api_view(request, forecast_id):
    try:
        forecast = ForecastModel.objects.get(pk=forecast_id)
        data = forecast.forecasted_data

        # Create a temporary directory to store JSON and CSV files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a JSON file
            json_file_path = f"{temp_dir}/forecast_data.json"
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=2)

            # Create a CSV file
            csv_file_path = f"{temp_dir}/forecast_data.csv"
            with open(csv_file_path, "w", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                for section, section_data in data.items():
                    csv_writer.writerow([section])
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            csv_writer.writerow([key, value])
                    else:
                        csv_writer.writerow([section_data])

            # Create a ZIP file
            zip_file_path = f"{temp_dir}/forecast_data.zip"
            with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(json_file_path, arcname="forecast_data.json")
                zip_file.write(csv_file_path, arcname="forecast_data.csv")

            # Read the ZIP file and serve it for download
            with open(zip_file_path, "rb") as zip_file:
                response = HttpResponse(zip_file.read(), content_type="application/zip")
                response["Content-Disposition"] = f'attachment; filename="{slugify(forecast.date)}.zip"'

        return response
    except ForecastModel.DoesNotExist:
        return HttpResponse("Forecast not found", status=404)


class ClearAllForecastAPIView(View):
    http_method_names = ['post']

    def post(self, request, industry_name):
        if not industry_name in (i['Industry'] for i in settings.INDUSTRIES):
            raise Http404('Industry does not exist')
        
        # Delete all user ForecastModel
        ForecastModel.objects.filter(user=request.user, industry=industry_name).delete()
        return redirect(reverse('main', kwargs={'industry_name': industry_name}))


class ForecastAPIView(APIView):
    def post(self, request, industry_name, format=None):
        # Check industry and get required data
        if not industry_name in (i['Industry'] for i in settings.INDUSTRIES):
            raise Http404('Industry does not exist')
        required_data = next((i['Attributes'] for i in settings.INDUSTRIES if i['Industry'] == industry_name), [])

        # Check if the uploaded file is a JSON or CSV file and not empty
        file = request.data.get('file')
        if not file:
            return Response({'message': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        if not (file.name.lower().endswith('.json') or file.name.lower().endswith('.csv')):
            return Response({'message': 'Invalid file uploaded. Upload CSV or JSON file.'}, status=status.HTTP_400_BAD_REQUEST)
        if file.size == 0:
            return Response({'message': 'No file data.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validates data format
        data = []
        try:
            if file.name.lower().endswith('.json'):
                data = json.loads(file.read().decode('utf-8'))
                if not isinstance(data, list):
                    return Response({'message': 'File content is not a JSON array.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                csv_data = file.read().decode('utf-8')
                csv_reader = csv.DictReader(csv_data.splitlines())
                for row in csv_reader:
                    data.append(row)
        except Exception:
            return Response({'message': 'Invalid data format.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if all required data names are in the data
        for d in data:
            for rd in required_data:
                if not rd['Name'] in d:
                    return Response({'message': f'Missing data: {rd["Name"]}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if data is 3 years or above
        if not len(data) > 35:
            return Response({'message': 'Minimum of 3 years data.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate if data contains all for a year
        # Create a defaultdict to store data by year and month
        data_dict = defaultdict(list)
        years = set()
        # Iterate through the data and group it by year and month
        for entry in data:
            date = entry["Date"]
            try:
                year, month = date.split("-")
                years.add(int(year))
            except ValueError:
                return Response({'message': f"Invalid date. Got \"{date}\"."}, status=status.HTTP_400_BAD_REQUEST)
            data_dict[(int(year), int(month))].append(entry)

        # Check if data contains all months for each year available
        start_year = min(years)
        end_year = max(years)
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (year, month) not in data_dict:
                    return Response({'message': f"Data missing for {year}-{month:02}"}, status=status.HTTP_400_BAD_REQUEST)

        # Perform LSTM model training and predicting
        training_set, _, _ = create_datasets(data)

        input_size = len(training_set[0][0])
        hidden_size = 64  # or any other appropriate size
        output_size = 1  # predicting revenue, a single value

        lstm = LSTM(input_size, hidden_size, output_size)
        lstm.train(training_set, epochs=100, learning_rate=0.001)
        predictions = lstm.predict(steps=12)

        # Prepare response
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        response_data = {
            'message': f'Month sales for year {end_year + 1} is calculated!',
            'predictions': predictions,
            'total_sales': sum(predictions),
            'highest_sales': (max(predictions), months[predictions.index(max(predictions))]), # max, month
            'lowest_sales': (min(predictions), months[predictions.index(min(predictions))]), # min, month
            'average_sales': round(sum(predictions) / 12),
            'predicted_year': end_year + 1,
            'success': True
        }

        # Make ForecastModel of the prediction if user is authenticated
        if request.user.is_authenticated:
            ForecastModel.objects.create(
                user=request.user,
                industry=industry_name,
                forecasted_data=response_data
            )

        return Response(response_data, status=status.HTTP_200_OK)