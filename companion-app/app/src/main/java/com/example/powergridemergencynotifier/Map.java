package com.example.powergridemergencynotifier;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.location.Address;
import android.location.Geocoder;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.view.Menu;
import android.view.MenuItem;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.Circle;
import com.google.android.gms.maps.model.CircleOptions;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;

import android.os.Handler;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

// Implement OnMapReadyCallback.
public class Map extends AppCompatActivity implements OnMapReadyCallback, GoogleMap.OnMarkerClickListener {
    double map_lat=0.00;
    double map_lon=0.00;
    GoogleMap mMap;
    LatLng area;
    boolean doubleBackToExitPressedOnce = false;
    Object MarkerCheck1="m", MarkerCheck2;
    Geocoder geocoder;
    List<Address> addresses;
    String time;
    String category;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Set the layout file as the content view.
        setContentView(R.layout.map);

        //allows back button
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);

        //calling stored lat and lon
        SharedPreferences coordinates = PreferenceManager.getDefaultSharedPreferences(this);
        String str_map_lat = coordinates.getString("lat", "");
        String str_map_lon = coordinates.getString("lon", "");

        //convert lat and lon to double
        map_lat = Double.parseDouble(str_map_lat);
        map_lon = Double.parseDouble(str_map_lon);

        // Get a handle to the fragment and register the callback.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                //back button
                finish();
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    public boolean onCreateOptionsMenu(Menu menu) {
        return true;
    }

    // Get a handle to the GoogleMap object and display marker.
    @Override
    public void onMapReady(GoogleMap googleMap) {

        googleMap.setOnMarkerClickListener(this);

        mMap = googleMap;
        mMap.clear();
        //center map around enter lat and lon
        area = new LatLng(map_lat, map_lon);
        mMap.moveCamera(CameraUpdateFactory.newLatLng(area));
        //add 25 mile radius circle for visualization
        Circle circle = mMap.addCircle(new CircleOptions()
                .center(area)
                .radius(40234)
                .strokeColor(Color.BLACK));
        //add marker for past
        mMap.addMarker(new MarkerOptions()
                    .position(new LatLng(map_lat, map_lon))
                    .title("Ice"))
                //color of marker to specify past or current
                .setIcon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_BLUE));
        //add marker for current
        mMap.addMarker(new MarkerOptions()
                        .position(new LatLng(map_lat+0.17, map_lon-0.01))
                        .title("Fire"))
                //color of marker to specify past or current
                .setIcon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED));
    }
    @Override
    public boolean onMarkerClick(Marker marker) {
        marker.showInfoWindow();  //show title of marker
        geocoder = new Geocoder(this,Locale.getDefault());
        try {
            //use lat and long of marker
            addresses = geocoder.getFromLocation(marker.getPosition().latitude, marker.getPosition().longitude, 1);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        if (marker.getTitle().equals( "Fire")){
            category = "Immediate"; //info for notifcation page
            time = "4:57pm";        // hardcoded for demo
        }else if (marker.getTitle().equals( "Ice")){
            category = "Moderate";
            time = "2:32pm";
        }
        String city = addresses.get(0).getLocality();  //find city that correlates to lat and lon
        SharedPreferences notif_page = PreferenceManager.getDefaultSharedPreferences(this);
        SharedPreferences.Editor editor = notif_page.edit();
        //store values to be used on notif page
        editor.putString("keyword", marker.getTitle());
        editor.putString("location", city);
        editor.putString("category", category);
        editor.putString("time", time);
        editor.apply();
        //open notif page
        Intent intent = new Intent(this, NotificationPage.class);
        startActivity(intent);
        return true;

    }

}
