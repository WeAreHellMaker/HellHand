/*
 *  Finger Hell (2023.07.27)
 *
 *  Pro Makers (www.hellmaker.kr)  
 *  Duke kim (nicebug@naver.com)
 */
#include<Servo.h>

#define FINGER_MAX        10
#define DEALY_SERVOMOVE   10

#define IDLETIME_MAX      60000    //  1 Mintue


enum default_finger_value
{
  RIGHT_FINGER1 = 0,
  RIGHT_FINGER2 = 0,
  RIGHT_FINGER3 = 180,
  RIGHT_FINGER4 = 0,
  RIGHT_FINGER5 = 180,

  LEFT_FINGER1 = 90,
  LEFT_FINGER2 = 0,
  LEFT_FINGER3 = 0,
  LEFT_FINGER4 = 180,
  LEFT_FINGER5 = 0
};



const int g_nFingerIO[FINGER_MAX] = { 2, 3, 4, 5, 6, 7, 8, 9, 10, 11  };
int g_nServoAngleTarget[FINGER_MAX] = 
{
  RIGHT_FINGER1, RIGHT_FINGER2, RIGHT_FINGER3, RIGHT_FINGER4, RIGHT_FINGER5,  
  LEFT_FINGER1, LEFT_FINGER2, LEFT_FINGER3, LEFT_FINGER4, LEFT_FINGER5 
};

int g_nServoAngleNow[FINGER_MAX] = {0,};

Servo Servo[FINGER_MAX];




unsigned long g_lIdleMillis = millis();


/*
 * 
 */
void CommandFingerServo( int pFingerNum, int pAngle) 
{
    //
    //  Check the Finger Number
    //
    if( pFingerNum < 1 && pFingerNum > FINGER_MAX ) 
    {
      
      Serial.println( "Wrong Finger Number Input");
      return;
    }

    //
    //  Check the Angler
    //
    if( pAngle < 0 && pAngle > 180 ) 
    {
      Serial.println( "Wrong Finger pAngle Input");      
      return;
    }

    //
    //  Check the Servo Finger Min / Max Value
    //

  
    //
    //  Run Servo 
    //
    //  ServoFinger[pFingerNum-1].write(pAngle);
    Servo[pFingerNum].write(pAngle);

    g_nServoAngleNow[ pFingerNum ] = pAngle;
 }



/*
 *
 */
void RunIdle()
{

  unsigned long currentMillis = millis();

  if( ( currentMillis - g_lIdleMillis ) >=  IDLETIME_MAX  )
  {
    g_lIdleMillis = millis();

    //  Serial.println("time");
    g_nServoAngleTarget[0] = RIGHT_FINGER1;
    g_nServoAngleTarget[1] = RIGHT_FINGER2;
    g_nServoAngleTarget[2] = RIGHT_FINGER3;
    g_nServoAngleTarget[3] = RIGHT_FINGER4;
    g_nServoAngleTarget[4] = RIGHT_FINGER5;

    g_nServoAngleTarget[5] = LEFT_FINGER1;
    g_nServoAngleTarget[6] = LEFT_FINGER2;
    g_nServoAngleTarget[7] = LEFT_FINGER3;
    g_nServoAngleTarget[8] = LEFT_FINGER4;
    g_nServoAngleTarget[9] = LEFT_FINGER5;    
  }
}


/*
 * 
 */
void setup() {

  Serial.begin(115200);

  //
  //  Servo Testing
  //


  //
  //  Setup Servo IO
  //  
  for(int i=0; i < FINGER_MAX; i++ )
  {
    Servo[i].attach(g_nFingerIO[i]); 
    
    CommandFingerServo( i, g_nServoAngleTarget[i] );
  }
    
  Serial.println("Hi made By Hell Maker");       
}

/*
 * 
 */
void loop() {

  bool bMoveServo = false;

  if (Serial.available() > 0) 
  {

    g_lIdleMillis = millis();

    //
    // Waiting \n
    //
    String strReceivedData = Serial.readStringUntil('\n'); 
    String strParsedCommand = strReceivedData.substring(0, 2);

    //
    //  FN Command (2Byte) + FingerNum (1Byte) + Angle (3Byte)
    //
    if (strParsedCommand.equals( "FN" )) {
      int nFingerNum  = strReceivedData.substring(2, 3).toInt();
      int nAngle      = strReceivedData.substring(3, 6).toInt();

      Serial.print( "Finger Num : " );              
      Serial.print( nFingerNum ); 

      Serial.print( " / Angle = " );
      Serial.println( nAngle );   

      //  CommandFingerServo( nFingerNum, nAngle );
      g_nServoAngleTarget[nFingerNum] = nAngle;      
    }
    //
    //  FR Command
    //
    else if (strParsedCommand.equals( "FR" )) {

      for( int i=0; i < 5; i ++ )
      {
        int nFingerNum  = strReceivedData.substring(2 + i*4, 3 + i*4).toInt();
        int nAngle      = strReceivedData.substring(3 + i*4, 6 + i*4).toInt();
        
        //  CommandFingerServo( nFingerNum, nAngle ); 
        g_nServoAngleTarget[nFingerNum] = nAngle;
      }     
    }
    //
    //  FL Command
    //
    else if (strParsedCommand.equals( "FL" )) {

      for( int i=0; i < 5; i ++ )
      {
        int nFingerNum  = strReceivedData.substring(2 + i*4, 3 + i*4).toInt();
        int nAngle      = strReceivedData.substring(3 + i*4, 6 + i*4).toInt();
        
        //  CommandFingerServo( nFingerNum, nAngle );
        g_nServoAngleTarget[nFingerNum] = nAngle;        
      }     
    }
    else
    {
      Serial.println( "Wrong Command Input");
    }
  } 

  //
  //  Move Servo Motor
  //
  for( int i=0; i < FINGER_MAX; i ++ )
  {
    if( g_nServoAngleTarget[i] > g_nServoAngleNow[i]  )
    {
      g_nServoAngleNow[i] ++;
    
      CommandFingerServo( i, g_nServoAngleNow[i] );

      bMoveServo = true;
    }
    else if( g_nServoAngleTarget[i] < g_nServoAngleNow[i]  )
    {
      g_nServoAngleNow[i] --;

      CommandFingerServo( i, g_nServoAngleNow[i] );

      bMoveServo = true;      
    }

  }

  if( bMoveServo )
  {
    delay( DEALY_SERVOMOVE );
  }

  RunIdle();
}
