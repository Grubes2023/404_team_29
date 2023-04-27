package com.example.powergridemergencynotifier;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.location.Address;
import android.location.Geocoder;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import java.io.IOException;
import java.util.List;
import java.util.Locale;


public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    boolean isAvailable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        getSupportActionBar().hide();
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); //xml file connected to class

        Button button1 = findViewById(R.id.button1);
        button1.setOnClickListener(this);  //listener for submit button

        //if any stored zipcode from user open different page
        SharedPreferences coordinates = PreferenceManager.getDefaultSharedPreferences(this);
        String value = coordinates.getString("lat", ""); //check zipcode storage

        if(value!=null && !value.equals("")){ //if not empty
            //Re-Direct to new home screen
            Intent intent0 = new Intent(this, Options.class);
            startActivity(intent0);
        }
    }
    public static boolean isNetworkOnline2() {
        boolean isOnline = false;
        try {
            Runtime runtime = Runtime.getRuntime();
            Process p = runtime.exec("ping -c 1 8.8.8.8");
            int waitFor = p.waitFor();
            isOnline = waitFor == 0;    // only when the waitFor value is zero, the network is online indeed

        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        return isOnline;
    }
    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.button1: //submit button pressed
                final EditText zip_in =  findViewById(R.id.zipcode); //allow user to enter zipcode
                String zipcode = zip_in.getText().toString();  //convert zipcode to string
                if (zipcode.length() == 5){ //checking zip code is appropriate length
                    if (isNetworkOnline2()) { //check network is online
                        // Execution here
                        final Geocoder geocoder = new Geocoder(this);
                        try {
                            List<Address> addresses = geocoder.getFromLocationName(zipcode, 1);
                            if (addresses != null && !addresses.isEmpty()) {
                                Address address = addresses.get(0);
                                // Use the address as needed
                                double main_lat = address.getLatitude(); //conv to lat
                                double main_lon = address.getLongitude(); //conv to long

                                //convert double to string
                                String string_lat = String.valueOf(main_lat);
                                String string_lon = String.valueOf(main_lon);

                                //store lat and lon for future use
                                SharedPreferences coordinates = PreferenceManager.getDefaultSharedPreferences(this);
                                SharedPreferences.Editor editor = coordinates.edit();
                                editor.putString("lat", string_lat);
                                editor.putString("lon", string_lon);
                                editor.apply();

                                //output lat and lon
                                String message = String.format(Locale.US,"Latitude: %f, Longitude: %f",
                                        main_lat, main_lon);
                                Toast.makeText(this, message, Toast.LENGTH_LONG).show();

                                //open next page
                                Intent intent1 = new Intent(this, Options.class);
                                startActivity(intent1);

                            } else {
                                // Display appropriate message when Geocoder services are not available
                                Toast.makeText(this, "Invalid zipcode", Toast.LENGTH_LONG).show();
                            }
                        } catch (IOException e) {
                            // handle exception
                        }
                        break;
                    }

                    else {
                        // Error message here if network is unavailable.
                        Toast.makeText(this, "Network is unavailable!", Toast.LENGTH_LONG).show();
                    }

                }
                //zipcode is not correct length
                else{
                    Toast.makeText(MainActivity.this, "need 5 digit zipcode", Toast.LENGTH_LONG).show();
                    break;
                }
            default:
                break;
        }
    }
}
