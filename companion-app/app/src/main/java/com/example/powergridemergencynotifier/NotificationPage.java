package com.example.powergridemergencynotifier;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class NotificationPage extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Set the layout file as the content view.
        setContentView(R.layout.notif);

        //show action bar for back button visibility
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);

        SharedPreferences notif_page = PreferenceManager.getDefaultSharedPreferences(this);
        //retrieve stored data to display on page
        String time = notif_page.getString("time", "");
        String category = notif_page.getString("category", "");
        String keyword = notif_page.getString("keyword", "");
        String location = notif_page.getString("location", "");
        String date = notif_page.getString("date", "");
        //making var for text views on page
        TextView tv1 = findViewById(R.id.textView1);
        TextView tv2 = findViewById(R.id.textView2);
        TextView tv3 = findViewById(R.id.textView3);
        TextView tv4 = findViewById(R.id.time_col);
        //adding stored data into text views
        tv1.setText(category);
        tv2.setText(keyword);
        tv3.setText(location);
        tv4.setText(time);
    }
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            //back button
            case android.R.id.home:
                finish();
                return true;
        }
        return super.onOptionsItemSelected(item);
    }
    public boolean onCreateOptionsMenu(Menu menu) {
        return true;
    }
}
