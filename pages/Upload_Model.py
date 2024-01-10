import streamlit as st
import numpy as np
import tensorflow as tf
import onnxruntime
import tempfile
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def load_mnist_test_data():
    # Load the MNIST dataset
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    # Normalize the data to range [0, 1]
    x_test = x_test / 255.0

    return x_test, y_test


def test_model(model_path):
    # Load the ONNX model
    sess = onnxruntime.InferenceSession(model_path)
        
    # Get the model's input name
    input_name = sess.get_inputs()[0].name

    # Load the MNIST test dataset
    test_images, test_labels = load_mnist_test_data()

    # Perform inference on the test dataset
    predictions = []
    for image in test_images:
        input_data = np.expand_dims(image, axis=0).astype(np.float32)
        input_data = np.expand_dims(input_data, axis=1)  # Add Batch dimension
        pred = sess.run(None, {input_name: input_data})
        predictions.append(np.argmax(pred[0]))

    return predictions, test_labels, test_images

def evaluate_model(predictions, ground_truth_labels):
    accuracy = tf.keras.metrics.Accuracy()
    precision = tf.keras.metrics.Precision()
    recall = tf.keras.metrics.Recall()

    # Update the metrics with the predictions and ground truth labels
    accuracy.update_state(ground_truth_labels, predictions)
    precision.update_state(ground_truth_labels, predictions)
    recall.update_state(ground_truth_labels, predictions)

    # Get the computed metric values
    accuracy_value = float(accuracy.result().numpy())
    precision_value = float(precision.result().numpy())
    recall_value = float(recall.result().numpy())

    # Get the confusion Matrix
    cm = tf.math.confusion_matrix(ground_truth_labels, predictions)

    return accuracy_value, precision_value, recall_value, cm

def show():
    # Loading session state variables
    if 'users' and 'results' not in st.session_state:
        st.error("Couldn't connect to database.")

    if 'Logged_in' and 'userName' not in st.session_state:
        st.error("Please login to view this page")

    else:
        users = st.session_state["users"]
        results = st.session_state["results"]

        Logged_in = st.session_state["Logged_in"]
        userName = st.session_state["userName"]

        st.title("Model Upload")
        st.text(f"Hello {userName} in this page you can upload your model and take part of the compettion")

        # Upload ONNX model file
        st.subheader("Upload your ONNX Model")
        model_file = st.file_uploader("Choose an ONNX model file", type=["onnx"])

        # Test the model if uploaded
        if model_file is not None:
            st.success("Model uploaded successfully!")
            # Create a temporary file to save the uploaded model

            with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
                temp_model_path = temp_model_file.name
                temp_model_file.write(model_file.read())

            # Test the model and get predictions and ground truth labels
            predictions, ground_truth_labels, test_images = test_model(temp_model_path)

            # Plot the first 9 test images
            num_images_to_plot = 9
            fig, axs = plt.subplots(3, 3, figsize=(8, 8))
            fig.suptitle("MNIST Test Predictions", fontsize=16)

            for i in range(num_images_to_plot):
                ax = axs[i // 3, i % 3]
                ax.imshow(test_images[i], cmap='gray')
                ax.axis('off')
                ax_title = f"Predicted: {predictions[i]}, Ground Truth: {ground_truth_labels[i]}"
                if predictions[i] == ground_truth_labels[i]:
                    ax.set_title(ax_title, color='green')
                else:
                    ax.set_title(ax_title, color='red')

            # Adjust layout and display the plot
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            st.pyplot(fig)

            # Evaluating the model
            accuracy_value, precision_value, recall_value, cm = evaluate_model(predictions, ground_truth_labels)
            evaluation = {"User Name": userName,"Accuracy": accuracy_value, "Precision": precision_value, "Recall":recall_value}
            results.insert_one(evaluation)

            # Convert confusion matrix to a DataFrame for easier visualization
            cm_df = pd.DataFrame(cm)

            # Visualizing the Confusion matrix
            plt.figure(figsize=(10, 8))
            plt.title("Confusion Matrix", fontsize=16)

            sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", square=True)
            plt.xlabel("Predicted Label")
            plt.ylabel("True Label")
            st.pyplot(plt)

            st.success("Evaluation is done, see your score on the score page!!")

            # Delete the temporary file after testing
            os.remove(temp_model_path)

show()