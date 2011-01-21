package net.jong10.rosetta;

public class RosettaCallback {
	private static RosettaCallback uniqueInstance = new RosettaCallback();
	public static RosettaCallback getInstance() {
		return uniqueInstance;
	}
	public native void initialize();
	
	static {
		System.loadLibrary("rosetta-jni");
	}
}
