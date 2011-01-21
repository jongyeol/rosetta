package net.jong10.rosetta;

import android.content.Context;
import android.widget.Toast;

public class CallbackSample {
	private static CallbackSample uniqueInstance = new CallbackSample();
	private Context context;
	
	public static CallbackSample getInstance() {
		return uniqueInstance;
	}
	
	public void setContext(Context context) {
		this.context = context;
	}
	
	public void showToast(String text, int duration) {
		Toast.makeText(context, text, duration).show();
	}
}
