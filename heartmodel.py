# content from:
# https://keras.io/examples/structured_data/structured_data_classification_from_scratch/
# may be hitting the same bug as:
# https://github.com/keras-team/autokeras/issues/973

import os

# TensorFlow is the only backend that supports string inputs.
os.environ["KERAS_BACKEND"] = "tensorflow"

import tensorflow as tf
import pandas as pd
import keras
from keras import layers

file_url = "http://storage.googleapis.com/download.tensorflow.org/data/heart.csv"
dataframe = pd.read_csv(file_url)

val_dataframe = dataframe.sample(frac=0.2, random_state=1337)
train_dataframe = dataframe.drop(val_dataframe.index)

def dataframe_to_dataset(dataframe):
	dataframe = dataframe.copy()
	labels = dataframe.pop("target")
	ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
	ds = ds.shuffle(buffer_size=len(dataframe))
	return ds

train_ds = dataframe_to_dataset(train_dataframe)
val_ds = dataframe_to_dataset(val_dataframe)

train_ds = train_ds.batch(32)
val_ds = val_ds.batch(32)

def encode_numerical_feature(feature, name, dataset):
	# Create a Normalization layer for our feature
	normalizer = layers.Normalization()

	# Prepare a Dataset that only yields our feature
	feature_ds = dataset.map(lambda x, y: x[name])
	feature_ds = feature_ds.map(lambda x: tf.expand_dims(x, -1))

	# Learn the statistics of the data
	normalizer.adapt(feature_ds)

	# Normalize the input feature
	encoded_feature = normalizer(feature)
	return encoded_feature


def encode_categorical_feature(feature, name, dataset, is_string):
	lookup_class = layers.StringLookup if is_string else layers.IntegerLookup
	# Create a lookup layer which will turn strings into integer indices
	lookup = lookup_class(output_mode="binary")

	# Prepare a Dataset that only yields our feature
	feature_ds = dataset.map(lambda x, y: x[name])
	feature_ds = feature_ds.map(lambda x: tf.expand_dims(x, -1))

	# Learn the set of possible string values and assign them a fixed integer index
	lookup.adapt(feature_ds)

	# Turn the string input into integer indices
	encoded_feature = lookup(feature)
	return encoded_feature

# Categorical features encoded as integers
sex = keras.Input(shape=(1,), name="sex", dtype="int64")
cp = keras.Input(shape=(1,), name="cp", dtype="int64")
fbs = keras.Input(shape=(1,), name="fbs", dtype="int64")
restecg = keras.Input(shape=(1,), name="restecg", dtype="int64")
exang = keras.Input(shape=(1,), name="exang", dtype="int64")
ca = keras.Input(shape=(1,), name="ca", dtype="int64")

# Categorical feature encoded as string
thal = keras.Input(shape=(1,), name="thal", dtype="string")

# Numerical features
age = keras.Input(shape=(1,), name="age")
trestbps = keras.Input(shape=(1,), name="trestbps")
chol = keras.Input(shape=(1,), name="chol")
thalach = keras.Input(shape=(1,), name="thalach")
oldpeak = keras.Input(shape=(1,), name="oldpeak")
slope = keras.Input(shape=(1,), name="slope")

all_inputs = [
	age,
	ca,
	chol,
	cp,
	exang,
	fbs,
	oldpeak,
	restecg,
	sex,
	slope,
	thal,
	thalach,
	trestbps,
]

# Integer categorical features
sex_encoded = encode_categorical_feature(sex, "sex", train_ds, False)
cp_encoded = encode_categorical_feature(cp, "cp", train_ds, False)
fbs_encoded = encode_categorical_feature(fbs, "fbs", train_ds, False)
restecg_encoded = encode_categorical_feature(restecg, "restecg", train_ds, False)
exang_encoded = encode_categorical_feature(exang, "exang", train_ds, False)
ca_encoded = encode_categorical_feature(ca, "ca", train_ds, False)

# String categorical features
thal_encoded = encode_categorical_feature(thal, "thal", train_ds, True)

# Numerical features
age_encoded = encode_numerical_feature(age, "age", train_ds)
trestbps_encoded = encode_numerical_feature(trestbps, "trestbps", train_ds)
chol_encoded = encode_numerical_feature(chol, "chol", train_ds)
thalach_encoded = encode_numerical_feature(thalach, "thalach", train_ds)
oldpeak_encoded = encode_numerical_feature(oldpeak, "oldpeak", train_ds)
slope_encoded = encode_numerical_feature(slope, "slope", train_ds)

all_features = layers.concatenate(
	[
		sex_encoded,
		cp_encoded,
		fbs_encoded,
		restecg_encoded,
		exang_encoded,
		slope_encoded,
		ca_encoded,
		thal_encoded,
		age_encoded,
		trestbps_encoded,
		chol_encoded,
		thalach_encoded,
		oldpeak_encoded,
	]
)
x = layers.Dense(32, activation="relu")(all_features)
x = layers.Dropout(0.5)(x)
output = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(all_inputs, output)
model.compile("adam", "binary_crossentropy", metrics=["accuracy"])

model.fit(train_ds, epochs=50, validation_data=val_ds)

sample = {
	"age": 60,
	"sex": 1,
	"cp": 1,
	"trestbps": 145,
	"chol": 233,
	"fbs": 1,
	"restecg": 2,
	"thalach": 150,
	"exang": 0,
	"oldpeak": 2.3,
	"slope": 3,
	"ca": 0,
	"thal": "fixed",
}

input_dict = {name: tf.convert_to_tensor([value]) for name, value in sample.items()}
predictions = model.predict(input_dict)

print(
	f"This particular patient had a {100 * predictions[0][0]:.1f} "
	"percent probability of having a heart disease, "
	"as evaluated by our model."
)

