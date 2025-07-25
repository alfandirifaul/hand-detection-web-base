#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// --- WiFi Credentials ---
// Replace with your network's SSID and password
const char* ssid = "nesyaaa";
const char* password = "aaaaaaab";

// --- Web Server Setup ---
ESP8266WebServer server(80);
String latestMessage = "Waiting for commands..."; // Stores the most recent message to display

// --- State and Timer Variables ---
String command;
String lastCommand = "";
String lampState = "off"; // Initial state is off
unsigned long previousBlinkMillis = 0;
const long blinkInterval = 500; // Blink speed in milliseconds
int ledPinState = HIGH; // HIGH is off for the built-in LED

// --- Debounce/Cooldown Timer for Serial Commands ---
unsigned long lastProcessTime = 0;
const long commandCooldown = 1500; // Ignore new commands for 1.5 seconds after one is processed

// --- HTML page content ---
// Stored in PROGMEM to save RAM.
// The JavaScript has been corrected to only update the text when the data changes.
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP8266 Live Status</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f0f2f5; margin: 0; }
        .container { background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 90%; }
        h1 { color: #1c1e21; margin-bottom: 1.5rem; }
        #status-box { background-color: #e7f3ff; border: 1px solid #cfe2f3; padding: 1rem; border-radius: 8px; min-height: 50px; display: flex; justify-content: center; align-items: center; transition: background-color 0.3s; }
        #message { font-size: 1.2rem; color: #333; font-family: 'Courier New', Courier, monospace; }
        footer { margin-top: 1.5rem; font-size: 0.8rem; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP8266 Live Status</h1>
        <div id="status-box">
            <p id="message">Connecting...</p>
        </div>
        <footer>Page served directly from the ESP8266.</footer>
    </div>
    <script>
        // This variable is declared *outside* the interval function
        // so it remembers its value between calls.
        let lastData = "";

        setInterval(function() {
            fetch('/data')
                .then(response => response.text())
                .then(data => {
                    // Only update the page content if the data has actually changed.
                    if (lastData !== data) {
                        console.log("New data received:", data);
                        document.getElementById('message').textContent = data;
                        lastData = data; // Remember the new data.
                    }
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('message').textContent = 'Connection error';
                });
        }, 1500); // Update every 1.5 seconds
    </script>
</body>
</html>
)rawliteral";

// --- Web Server Handler Functions ---

// Function to serve the main HTML page
void handleRoot() {
  server.send(200, "text/html", INDEX_HTML);
}

// Function to serve the latest data
void handleData() {
  server.send(200, "text/plain", latestMessage);
}

// --- Main Setup Function ---
void setup() {
  // --- Basic Setup ---
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); // Start with LED off

  // --- WiFi Connection ---
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP()); // Print the IP address to find the device

  // --- Start Web Server ---
  server.on("/", handleRoot);   // Route for the main page
  server.on("/data", handleData); // Route to get live data
  server.begin();
  Serial.println("HTTP server started. Open the IP in your browser.");
  
  latestMessage = "ESP8266 Ready. Send 'green' or 'red' via Serial Monitor.";
}

// --- Main Loop Function ---
void loop() {
  // This is critical! It allows the server to process incoming client requests.
  server.handleClient();

  // --- Debounced Command Logic ---
  
  // Only check for new commands if the cooldown period has passed.
  if (millis() - lastProcessTime > commandCooldown) {
    if (Serial.available() > 0) {
      command = Serial.readStringUntil('\n');
      command.trim(); // Remove any whitespace

      // We only act on valid commands.
      if (command.equals("green") || command.equals("red")) {
        
        // Only change state if the command is new to prevent redundant processing
        if (!command.equals(lastCommand)) {
            Serial.println("Processing command: " + command);
            if (command.equals("green")) {
                lampState = "blinking";
                latestMessage = "Lamp State: BLINKING";
            } else { // It must be "red"
                lampState = "off";
                latestMessage = "Lamp State: OFF";
            }
            lastCommand = command; // Remember the last VALID command.
        }
        
        // IMPORTANT: Reset the cooldown timer because we received a valid command.
        // This will trigger the buffer clearing logic below for the next 1.5s.
        lastProcessTime = millis(); 

      } else if (command.length() > 0) {
        // If we receive junk like "greengreen", we log it but do nothing else.
        // Crucially, we DO NOT reset the cooldown timer. This allows the system
        // to recover and look for a valid command immediately in the next loop.
        Serial.println("Ignoring unknown data: " + command);
      }
    }
  } else {
    // During the cooldown period, read and discard any data in the serial buffer
    // to ignore the rest of the burst from Node-RED.
    while (Serial.available() > 0) {
      Serial.read();
    }
  }

  // 2. Update the physical LED based on the current state
  if (lampState.equals("blinking")) {
    unsigned long currentMillis = millis();
    if (currentMillis - previousBlinkMillis >= blinkInterval) {
      previousBlinkMillis = currentMillis;
      // Invert the LED state
      ledPinState = (ledPinState == LOW) ? HIGH : LOW;
      digitalWrite(LED_BUILTIN, ledPinState);
    }
  } else if (lampState.equals("off")) {
    // Keep the LED off (HIGH is off for the built-in LED)
    digitalWrite(LED_BUILTIN, HIGH);
  }
}
