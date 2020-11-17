#include <ArduinoJson.h>
#include <TroykaDHT.h>

bool handshaked;

DHT dht(8, DHT11);


void setup() {
    Serial.begin(9600);
    dht.begin();
    randomSeed(analogRead(0));
}

void loop() {
    if (!handshaked) {
        connect();
    }

    send_data();
    delay(100);
}

void connect() {
    do {
        Serial.println("__transmitting");
        Serial.flush();
        delay(1000);
    }
    while (Serial.readString() != "__received\r\n" && Serial.available());

    handshaked = true;
    Serial.flush();
}

void send_data() {
    StaticJsonDocument<200> doc;

    dht.read();
    if (dht.getState() == DHT_OK) {
        doc["temp"] = dht.getTemperatureC();
        doc["humi"] = dht.getHumidity();
    }
    else {
        doc["temp"] = "NaN";
        doc["humi"] = "NaN";
    }

    serializeJson(doc, Serial);
    Serial.println();
    delay(1000);
}
