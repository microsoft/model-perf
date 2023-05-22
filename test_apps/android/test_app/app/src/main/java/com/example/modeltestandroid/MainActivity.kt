package com.example.modeltestandroid

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresApi
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.File
import java.lang.Exception

class MainActivity : AppCompatActivity() {

    // UI Views
    private lateinit var startBtn: Button
    private lateinit var dataDirTextInput: EditText

    private companion object {
        private const val STORAGE_PERMISSION_CODE = 100
        private const val TAG = "PERMISSION_TAG"
    }

    init {
        System.loadLibrary("android_test_app_jni")
    }

    external fun testModelFromJNI(config_path: String)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        startBtn = findViewById(R.id.button_start)
        dataDirTextInput = findViewById(R.id.text_input_data_dir)


        // request all files permission
        if(checkStoragePermission()) {
            Log.d(TAG, "onCreate: permission already granted")
        }
        else {
            Log.d(TAG, "onCreate: permission not granted, request permission")
            requestPermission()
        }
        var dataDir = Environment.getExternalStorageDirectory().path + "/ModelTest/data"
        dataDirTextInput.setText(dataDir)

        startBtn.setOnClickListener {
            testModelFromJNI("${dataDirTextInput.text}/config.json")
        }
    }

    private fun checkStoragePermission(): Boolean {
        return if(Build.VERSION.SDK_INT > Build.VERSION_CODES.R) {
            // Android is 11(R) or above
            Environment.isExternalStorageManager()
        } else {
            // Android is below 11(R)
            val write = ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
            val read = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
            write == PackageManager.PERMISSION_GRANTED && read == PackageManager.PERMISSION_GRANTED
        }
    }

    private fun requestPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android is 11(R) above
            try {
                Log.d(TAG, "requestPermission: try")
                val intent = Intent()
                intent.action = Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION
                val uri = Uri.fromParts("package", this.packageName, null)
                intent.data = uri
                storageActivityResultLauncher.launch(intent)
            } catch (e: Exception) {
                Log.e(TAG, "requestPermission: ", e)
                val intent = Intent()
                intent.action = Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION
                storageActivityResultLauncher.launch(intent)
            }
        } else {
            // Android is below R
            ActivityCompat.requestPermissions(
                this,
                arrayOf(
                    Manifest.permission.WRITE_EXTERNAL_STORAGE,
                    Manifest.permission.READ_EXTERNAL_STORAGE
                ),
                STORAGE_PERMISSION_CODE
            )
        }
    }

    @RequiresApi(Build.VERSION_CODES.R)
    private val storageActivityResultLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        if (Environment.isExternalStorageManager()) {
            Log.d(TAG, "storageActivityResultLauncher: ")
        } else {
            Toast.makeText(this, "Request to Access All File Denied", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode != STORAGE_PERMISSION_CODE) {
            return
        }
        if (grantResults.isNotEmpty() &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            Log.d(TAG, "onRequestPermissionsResult: granted")
        } else {
            Toast.makeText(this, "Request to Access All File Denied", Toast.LENGTH_SHORT).show()
        }
    }
}