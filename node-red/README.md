# Hand Detection Project

This project implements a hand detection system using Python and Node-Red. The system captures video from a camera, detects hands using MediaPipe, counts the number of fingers, and sends this data to a Node-Red dashboard for visualization.

## Project Structure

```
hand-detection-project
├── python
│   ├── main.py               # Main entry point of the application
│   ├── camera.py             # Camera handling class
│   ├── handDetection.py       # Hand detection class using MediaPipe
│   ├── nodeRedClient.py       # Client for sending data to Node-Red
│   └── requirements.txt       # Python dependencies
├── node-red
│   ├── flows.json            # Node-Red flow configuration
│   └── README.md             # Documentation for Node-Red setup
└── README.md                 # General project documentation
```

## Setup Instructions

1. **Install Python Dependencies**:
   Navigate to the `python` directory and install the required packages using the following command:
   ```
   pip install -r requirements.txt
   ```

2. **Run the Python Application**:
   Execute the `main.py` script to start the hand detection application:
   ```
   python main.py
   ```

3. **Set Up Node-Red**:
   - Install Node-Red if you haven't already.
   - Import the `flows.json` file into Node-Red to set up the necessary flows.
   - Start Node-Red and access the dashboard to visualize the video feed and finger count.

## Usage

Once the Python application is running and Node-Red is set up, you will see the video feed from your camera along with the detected hand landmarks and the count of fingers displayed on the Node-Red dashboard.

## License

This project is licensed under the MIT License.