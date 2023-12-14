import numpy as np
from secrets import choice


class Dataset:
    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets


    def __len__(self):
        """Return the size of the dataset"""
        return len(self.targets)


    def __getitem__(self, index):
        """Retrieve inputs and targets at the given index"""
        x = self.inputs[index]
        y = self.targets[index]
        return x, y


def create_datasets(sequences):
    """
    Splits a list of sequences into training, validation, and test datasets.

    Args:
        sequences: A list of sequences, where each sequence is a list of elements.
    """
    # Encode date numerically and make sure that Revenue and Date value are the first one in data
    nd = []
    for d in sequences:
        year, month = d['Date'].split('-')
        numerical_date = int(year) + (int(month) / 100.0)
        l = [d['Revenue'], numerical_date]
        for k, v in d.items():
            if not k in ['Revenue', 'Date']:
                l.append(v)
        nd.append(l)

    # Define partition sizes
    num_train = int(len(nd) * 0.8) # 80%
    num_val = int(len(nd) * 0.1) # 10%
    num_test = int(len(nd) * 0.1) # 10%

    # Split sequences into partitions
    sequences_train = nd[:num_train]
    sequences_val = nd[num_train:num_train + num_val]
    sequences_test = nd[-num_test:]

    def get_inputs_targets_from_sequences(sequences):
        # Define empty lists
        inputs, targets = [], []
        
        for i, sequence in enumerate(sequences):
            inputs.append([sequence[0]])
            try:
                targets.append([sequences[i + 1][0]])
            except IndexError:
                pass

        return inputs, targets

    # Get inputs and targets for each partition
    inputs_train, targets_train = get_inputs_targets_from_sequences(sequences_train)
    inputs_val, targets_val = get_inputs_targets_from_sequences(sequences_val)
    inputs_test, targets_test = get_inputs_targets_from_sequences(sequences_test)

    # Create datasets
    training_set = Dataset(inputs_train, targets_train)
    validation_set = Dataset(inputs_val, targets_val)
    test_set = Dataset(inputs_test, targets_test)

    return training_set, validation_set, test_set


class LSTM:
    
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.r_min = 0
        self.r_max = 0

        # Xavier/Glorot initialization
        self.Wf = np.random.randn(hidden_size, input_size + hidden_size) * np.sqrt(2.0 / (input_size + hidden_size))
        self.bf = np.zeros((hidden_size, 1))

        self.Wi = np.random.randn(hidden_size, input_size + hidden_size) * np.sqrt(2.0 / (input_size + hidden_size))
        self.bi = np.zeros((hidden_size, 1))

        self.Wc = np.random.randn(hidden_size, input_size + hidden_size) * np.sqrt(2.0 / (input_size + hidden_size))
        self.bc = np.zeros((hidden_size, 1))

        self.Wo = np.random.randn(hidden_size, input_size + hidden_size) * np.sqrt(2.0 / (input_size + hidden_size))
        self.bo = np.zeros((hidden_size, 1))

        self.Wy = np.random.randn(output_size, hidden_size) * np.sqrt(2.0 / hidden_size)
        self.by = np.zeros((output_size, 1))

        # Memory cells
        self.c = np.zeros((hidden_size, 1))
        self.h = np.zeros((hidden_size, 1))


    def sigmoid(self, x, derivative=False):
        if derivative:
            return x * (1 - x)
        return 1 / (1 + np.exp(-x))


    def tanh(self, x, derivative=False):
        if derivative:
            return 1 - np.tanh(x) ** 2
        return np.tanh(x)


    def forward(self, x):
        m = np.vstack((self.h, x))
        f = self.sigmoid(np.dot(self.Wf, m) + self.bf)
        i = self.sigmoid(np.dot(self.Wi, m) + self.bi)
        c_bar = self.tanh(np.dot(self.Wc, m) + self.bc)
        self.c = f * self.c + i * c_bar
        o = self.sigmoid(np.dot(self.Wo, m) + self.bo)
        self.h = o * self.tanh(self.c)
        y = np.dot(self.Wy, self.h) + self.by
        return y


    def backward(self, x, y, y_pred, learning_rate=0.01):
        # Calculate gradients
        dy = y_pred - y
        dWy = np.dot(dy, self.h.T)
        dby = dy

        dh = np.dot(self.Wy.T, dy)
        do = dh * self.tanh(self.c)
        do = self.sigmoid(self.h, derivative=True) * do
        dWo = np.dot(do, np.vstack((self.h, x)).T)
        dbo = do

        dc = dh * self.h
        dc = self.tanh(self.c, derivative=True) * dc
        dc_bar = dc * self.sigmoid(np.dot(self.Wi, np.vstack((self.h, x))) + self.bi)
        dc_bar = self.tanh(np.dot(self.Wc, np.vstack((self.h, x))) + self.bc, derivative=True) * dc_bar
        dWc = np.dot(dc_bar, np.vstack((self.h, x)).T)
        dbc = dc_bar

        di = dc * self.c
        di = self.sigmoid(np.dot(self.Wi, np.vstack((self.h, x))) + self.bi, derivative=True) * di
        dWi = np.dot(di, np.vstack((self.h, x)).T)
        dbi = di

        df = dc * self.c
        df = self.sigmoid(np.dot(self.Wf, np.vstack((self.h, x))) + self.bf, derivative=True) * df
        dWf = np.dot(df, np.vstack((self.h, x)).T)
        dbf = df

        # Update weights and biases
        self.Wy -= learning_rate * dWy
        self.by -= learning_rate * dby
        self.Wo -= learning_rate * dWo
        self.bo -= learning_rate * dbo
        self.Wc -= learning_rate * dWc
        self.bc -= learning_rate * dbc
        self.Wi -= learning_rate * dWi
        self.bi -= learning_rate * dbi
        self.Wf -= learning_rate * dWf
        self.bf -= learning_rate * dbf


    def train(self, dataset, epochs=100, learning_rate=0.01):
        for _ in range(epochs):
            total_loss = 0
            for x, y in dataset:
                r = int(x[0])
                if r > self.r_max:
                    self.r_max = r
                if r < self.r_min:
                    self.r_min = r

                x, y = np.array(x).reshape(-1, 1), np.array(y).reshape(-1, 1)
                y_pred = self.forward(x)
                loss = np.mean((y_pred - y) ** 2)
                total_loss += loss
                self.backward(x, y, y_pred, learning_rate)


    def predict(self, steps=12):
        predictions = []
        for _ in range(steps):
            x = self.h.T  # Transposing to make it (1, hidden_size)
            if self.input_size != self.hidden_size:
                # You might need a different transformation depending on your use case
                x = x[:, :self.input_size]  # Trimming or transforming the input if necessary
            x = x.T  # Transposing back to make it (input_size, 1)
            y_pred = self.forward(x)
            predictions.append(y_pred.flatten())  # Flattening to turn it back into a 1D array
        return [round(p[0] + choice(range(self.r_min, self.r_max))) for p in predictions]