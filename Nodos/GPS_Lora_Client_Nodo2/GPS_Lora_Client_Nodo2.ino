#include <SoftwareSerial.h>
#include <TinyGPS.h>
#include <SPI.h>
#include <RH_RF95.h>
#include <SimpleDHT.h>
#define DHT11_PIN A1

// Our RFM95 Configuration 
#define RF_FREQUENCY  868.00

#define RF_NODE_ID    2
uint8_t RF_GATEWAY_ID = 1;

// Create an instance of a driver
RH_RF95 rf95;

//int pinDHT11 = 2;
SimpleDHT11 dht11;

TinyGPS gps;
SoftwareSerial ss(3, 4); // Arduino TX, RX , 

static void smartdelay(unsigned long ms);
static void print_float(float val, float invalid, int len, int prec);
static void print_date(TinyGPS &gps);

String datastring="";
String datastring1="";
String datastring2="";
String node = "2";
uint8_t dataoutgoing[100];
uint8_t dataoutgoing1[50];
uint8_t dataoutgoing2[50];
uint8_t dataoutgoing3[50];
char gps_lon[20]={"\0"};  
char gps_lat[20]={"\0"}; 
char temp[20]={"\0"};

void setup()
{
  // initialize both serial ports:
  Serial.begin(9600);  // Serial to print out GPS info in Arduino IDE
  ss.begin(9600); // SoftSerial port to get GPS data. 
  while (!Serial) 
  if (!rf95.init()){
    Serial.println("init failed");}
  else{
    Serial.println("RF95 module seen OK!");
    rf95.available();
    rf95.setTxPower(14, false); 
    rf95.setFrequency( RF_FREQUENCY );
    // This is our Node ID
    rf95.setThisAddress(RF_NODE_ID);
    rf95.setHeaderFrom(RF_NODE_ID); 
    // Where we're sending packet
    rf95.setHeaderTo(RF_GATEWAY_ID);  

    printf("RF95 node #%d init OK @ %3.2fMHz\n", RF_NODE_ID, RF_FREQUENCY );
    }
  delay(1000);
  Serial.println("       Monitor Dragino LoRa GPS Shield Status       ");
  Serial.print("                     Testing TFM                      "); 
  Serial.println();
  Serial.println("   Date      Time   Latitude  Longitude  Temperature");
  Serial.println("                     (deg)      (deg)        (°C)   ");
  Serial.println("----------------------------------------------------");
  smartdelay(2000);
}

void loop()
{
  byte temperature = 0;
  byte humidity = 0;
  byte data[40] = {0};
  float flat, flon; // flat es la variable de latitud, flon es la variable de longitud
  unsigned long date, time;
  uint8_t Msg1[] = "Sending to rf95_server";
  uint8_t Msg2[] = "No hay señal de GPS";
  unsigned long ID_gateway;
  uint8_t latitud1 [] = "";
  
  dht11.read(DHT11_PIN, &temperature, &humidity, data);
  if (temperature!=0 || humidity!=0)
  {
    ID_gateway = (int)RF_GATEWAY_ID;
    print_date(gps);
    gps.f_get_position(&flat, &flon);
    print_float(flat, TinyGPS::GPS_INVALID_F_ANGLE, 10, 6);
    print_float(flon, TinyGPS::GPS_INVALID_F_ANGLE, 11, 6); 
    Serial.print("    ");
    print_int((int)temperature, 3);
    Serial.print("    ");
    print_str(Msg1, 22);
    Serial.println();
    flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6;          
    flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6; 
      // Once the GPS fixed,send the data to the server.
    datastring +=dtostrf(flat, 0, 6, gps_lat); //Conviert un número a char
    datastring1 +=dtostrf(flon, 0, 6, gps_lon);
    datastring2 +=dtostrf(temperature, 0, 0, temp);
     //strcpy: Sirve para copiar la cadena cadena2 dentro de cadena1
    strcpy((char *)dataoutgoing1,gps_lat); 
    strcpy((char *)dataoutgoing2,gps_lon);
    strcpy((char *)dataoutgoing3,temp);
    uint8_t dataoutgoing[100] = "";
    strcat(dataoutgoing, "2"); // El número 1 corresponde al node 1
    strcat(dataoutgoing, ",");
    strcat(dataoutgoing, dataoutgoing1);
    strcat(dataoutgoing, ",");
    strcat(dataoutgoing, dataoutgoing2);
    strcat(dataoutgoing, ",");
    strcat(dataoutgoing, dataoutgoing3);
    //Serial.println((char *)dataoutgoing);
    Serial.flush();
    ss.flush();
    // Send the data to server
    if(rf95.init())
    {
      rf95.setModeTx(); 
      rf95.send(dataoutgoing, sizeof(dataoutgoing));
      rf95.waitPacketSent();
      delay(1000);
    }
  //delay(2000);
  }
  else
  {
  Serial.println("Falla del gateway");
  delay(3000);
  }
}

static void smartdelay(unsigned long ms)
{
  unsigned long start = millis();
  do 
  {
    while (ss.available())
    {
      //ss.print(Serial.read());
      gps.encode(ss.read());
    }
  } while (millis() - start < ms);
}

static void print_float(float val, float invalid, int len, int prec)
{
  if (val == invalid)
  {
    while (len-- > 1)
      Serial.print('*');
    Serial.print(' ');
  }
  else
  {
    Serial.print(val, prec);
    int vi = abs((int)val);
    int flen = prec + (val < 0.0 ? 2 : 1); // . and -
    flen += vi >= 1000 ? 4 : vi >= 100 ? 3 : vi >= 10 ? 2 : 1;
    for (int i=flen; i<len; ++i)
      Serial.print(' ');
  }
  smartdelay(0);
}

static void print_date(TinyGPS &gps)
{
  int year;
  byte month, day, hour, minute, second, hundredths;
  unsigned long age;
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths, &age);
  if (age == TinyGPS::GPS_INVALID_AGE)
    Serial.print("********** ******** ");
  else
  {
    char sz[32];
    sprintf(sz, "%02d/%02d/%02d %02d:%02d:%02d ",
        month, day, year, hour, minute, second);
    Serial.print(sz);
  }
  smartdelay(0);
}

static void print_str(const char *str, int len)
{
  int slen = strlen(str);
  for (int i=0; i<len; ++i)
    Serial.print(i<slen ? str[i] : ' ');
  smartdelay(0);
}

static void print_int(unsigned long val, int len)
{
  char sz[32];
  sprintf(sz, "%ld", val);
  sz[len] = 0;
  for (int i=strlen(sz); i<len; ++i)
    sz[i] = ' ';
  if (len > 0) 
    sz[len-1] = ' ';
  Serial.print(sz);
  smartdelay(0);
}
