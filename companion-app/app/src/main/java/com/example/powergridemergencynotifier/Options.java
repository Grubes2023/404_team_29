package com.example.powergridemergencynotifier;

import android.content.SharedPreferences;
import android.location.Address;
import android.location.Geocoder;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import android.content.Intent;
import android.preference.PreferenceManager;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import com.google.android.material.navigation.NavigationView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class Options extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener, View.OnClickListener{

    public DrawerLayout drawerLayout;
    public ActionBarDrawerToggle actionBarDrawerToggle;
    public NavigationView navigationView;

    double map_lat=0.00;
    double map_lon=0.00;

    Geocoder geocoder;
    List<Address> addresses = new ArrayList();

    String city_current, city_past;

    private void setNavigationViewListener() {
        navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.options);
        setNavigationViewListener();  //listener for nav menu

        Button button1 = findViewById(R.id.button1);
        button1.setOnClickListener(this);  //listener for mapview button

        TableRow secondRow = findViewById(R.id.secondRow); //making rows clickable
        secondRow.setClickable(true);
        secondRow.setOnClickListener(this);

        TableRow firstRowCurrent = findViewById(R.id.thirdRow); //making rows clickable
        firstRowCurrent.setClickable(true);
        firstRowCurrent.setOnClickListener(this);

        // drawer layout instance to toggle the menu icon to open
        // drawer and back button to close drawer
        drawerLayout = findViewById(R.id.my_drawer_layout);
        actionBarDrawerToggle = new ActionBarDrawerToggle(this, drawerLayout, R.string.nav_open, R.string.nav_close);

        // pass the Open and Close toggle for the drawer layout listener
        // to toggle the button
        drawerLayout.addDrawerListener(actionBarDrawerToggle);
        actionBarDrawerToggle.syncState();

        // to make the Navigation drawer icon always appear on the action bar
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);

        SharedPreferences coordinates = PreferenceManager.getDefaultSharedPreferences(this);
        //retrieving stored location values
        String str_map_lat = coordinates.getString("lat", "");
        String str_map_lon = coordinates.getString("lon", "");

        //convert lat and lon to double
        map_lat = Double.parseDouble(str_map_lat);
        map_lon = Double.parseDouble(str_map_lon);

        //converting into city
        geocoder = new Geocoder(this, Locale.getDefault());
        try {
            addresses = geocoder.getFromLocation(map_lat, map_lon, 1); // Here 1 represent max location result to returned, by documents it recommended 1 to 5
        } catch (IOException e) {
            //catch for any problems
            throw new RuntimeException(e);
        }
        city_past = addresses.get(0).getLocality();

        //converting into city
        try {
            addresses = geocoder.getFromLocation(map_lat+0.17, map_lon-0.01, 1); // Here 1 represent max location result to returned, by documents it recommended 1 to 5
        } catch (IOException e) {
            //catch for any problems
            throw new RuntimeException(e);
        }
        city_current = addresses.get(0).getLocality();

        //create var for text views in table
        TextView tv1 = findViewById(R.id.cityPast);
        TextView tv2 = findViewById(R.id.cityCurrent);
        //add converted cities into text views
        tv1.setText(city_past);
        tv2.setText(city_current);
    }


    // override the onOptionsItemSelected()
    // function to implement
    // the item click listener callback
    // to open and close the navigation
    // drawer when the icon is clicked
    @Override
    public void onClick( View view ) {
        switch(view.getId()) {
            case R.id.secondRow: {
                SharedPreferences notif_page = PreferenceManager.getDefaultSharedPreferences(this);
                //store data to show on notification page
                SharedPreferences.Editor editor = notif_page.edit();
                editor.putString("time", "4:57pm");
                editor.putString("date", "04/27");
                editor.putString("category", "Immediate");
                editor.putString("keyword", "Fire");
                editor.putString("location", city_current);
                editor.apply();
                //open notif page
                Intent intent1 = new Intent(this, NotificationPage.class);
                startActivity(intent1);
                break;
            }
            case R.id.thirdRow: {
                SharedPreferences notif_page = PreferenceManager.getDefaultSharedPreferences(this);
                //store data to show on notif page
                SharedPreferences.Editor editor = notif_page.edit();
                editor.putString("time", "2:32pm");
                editor.putString("date", "04/25");
                editor.putString("category", "Moderate");
                editor.putString("keyword", "Ice");
                editor.putString("location", city_past);
                editor.apply();
                //open notif page
                Intent intent1 = new Intent(this, NotificationPage.class);
                startActivity(intent1);
                break;
            }
            case R.id.button1: {//mapView button pressed
                Intent intent2 = new Intent(this, Map.class);
                startActivity(intent2);
                break;
        }
        }
    }
    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {

        if (actionBarDrawerToggle.onOptionsItemSelected(item)) {
            //allow nav menu to toggle
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        // Handle navigation view item clicks here.
        switch (item.getItemId()) {

            case R.id.newzip: {
                SharedPreferences coordinates = PreferenceManager.getDefaultSharedPreferences(this);
                SharedPreferences.Editor editor = coordinates.edit();
                //clear lat and long for new input
                editor.putString("lat", "");
                editor.putString("lon", "");
                editor.apply();
                //open main activity page
                Intent intent1 = new Intent(this, MainActivity.class);
                startActivity(intent1);
                break;
            }
            case R.id.contact: {
                //open help page
                Intent intent3 = new Intent(this, Help.class);
                startActivity(intent3);
                break;
            }
        }
        //close navigation drawer
        drawerLayout.closeDrawer(GravityCompat.START);
        return true;
    }
}
