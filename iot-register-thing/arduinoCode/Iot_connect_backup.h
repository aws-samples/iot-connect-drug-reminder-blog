#include "secrets.h"
#include <WiFiClientSecure.h>
#include <MQTTClient.h>
#include <ArduinoJson.h>
#include "WiFi.h"
#include "ESPDateTime.h"



// The MQTT topics that this device should publish/subscribe
#define AWS_IOT_PUBLISH_TOPIC   "esp32/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/sub"

WiFiClientSecure net = WiFiClientSecure();
MQTTClient client = MQTTClient(256);

void connectAWS()
{
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.println("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  // Configure WiFiClientSecure to use the AWS IoT device credentials
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);

  // Connect to the MQTT broker on the AWS endpoint we defined earlier
  client.begin(AWS_IOT_ENDPOINT, 8883, net);

  // Create a message handler
  client.onMessage(messageHandler);

  Serial.print("Connecting to AWS IOT");

  while (!client.connect(THINGNAME)) {
    Serial.print(".");
    delay(100);
  }

  if(!client.connected()){
    Serial.println("AWS IoT Timeout!");
    return;
  }

  // Subscribe to a topic
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);

  Serial.println("AWS IoT Connected!");
}

void publishMessage()
{
  StaticJsonDocument<200> doc;
  DateTime.setTimeZone("EST-8");
  DateTime.begin();
  doc["time"] = DateTime.toISOString().c_str();
  
  doc["box_close"] = digitalRead(26);
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer); // print to client

  client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

void messageHandler(String &topic, String &payload) {
  Serial.println("incoming: " + topic + " - " + payload);

//  StaticJsonDocument<200> doc;
//  deserializeJson(doc, payload);
//  const char* message = doc["message"];
}

void setup() {
  Serial.begin(9600);
  pinMode(26, INPUT);
  pinMode(25, INPUT);
  connectAWS();
}

uint16_t analogRead_value = 0;
uint16_t analogRead_value_1 = 0;
uint16_t digitalRead_value = 0;
uint16_t digitalRead_value_1 = 0;
void loop() {
  publishMessage();
  analogRead_value = analogRead(36);
  analogRead_value_1 = analogRead(35);
  digitalRead_value = digitalRead(26);
  digitalRead_value_1 = digitalRead(25);
  //cur_recv_value = digitalRead(ir_recv_pin);
  client.loop();
  //Serial.println("Pin 36");
  //Serial.println(analogRead_value);
  //Serial.println("Pin 35");
  //Serial.println(analogRead_value_1);
  Serial.println("Pin Digital Values");
  Serial.println(digitalRead_value);

  //Serial.println("Pin 35");
  //Serial.println(analogRead_value_1);
  delay(5000);
}