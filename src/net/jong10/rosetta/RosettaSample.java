package net.jong10.rosetta;

import android.app.Activity;
import android.view.View;
import android.widget.TextView;
import android.os.Bundle;

public class RosettaSample extends Activity
{
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.rosetta_sample);
		
		////////////////////////////////////////////////////////////////////////////
		// 로제타 테스트 (Java 코드에서, C++ 코드를 호출하는 것)
		
		// int Sample::add(int a, int b)
		int added = Sample.getInstance().add(1, 2);
		
		// void Sample::printLog(char* tag, char* log)
		Sample.getInstance().printLog("ROSETTA", "this is log by Rosetta");
		
		// char* Sample::getString()
		String test = Sample.getInstance().getString();
		
		// output
		TextView tv = ((TextView)findViewById(R.id.rosetta_sample_text_view));
		tv.setText(added + "\n" + test);
		
		
		/////////////////////////////////////////////////////////////////////////////
		// 콜백 테스트 (C++ 코드에서, Java 코드를 호출하는 것)
		
		// prepare Callback
		RosettaCallback.getInstance().initialize();
		
		// 콜백 클래스 테스트를 위한 준비
		CallbackSample.getInstance().setContext(this);
	}
	
	public void onClickCallbackTest(View V) {
		// 이 메소드를 실행하면,
		// C++ 로 구현된 testCallback() 안에서,
		// Java의 CallbackSample.showToast() 를 실행한다.
		// 즉, C++ 코드에서, Java 코드를 호출한다.
		Sample.getInstance().testCallback();
	}
}
