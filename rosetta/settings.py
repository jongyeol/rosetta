#!/usr/bin/python
# -*- coding: utf-8 -*-

# Rosetta settings

LIB_NAME = 'rosetta-jni'

STD_INCLUDE_FILES = ['jni.h', 'assert.h']
USR_INCLUDE_FILES = ['rosetta.h']

PACKAGE = 'net.jong10.rosetta'
CPP_FILENAME = 'rosetta.cpp'

CALLBACK_CLASS = 'RosettaCallback'
CALLBACK_FILENAME = 'callback.cpp'
CALLBACK_HEADER_FILENAME = 'callback.h'

# C++ 에서 별도의 클래스를 만들어서, Rosetta.h에서 헤더를 include한다.
# 해당 클래스는 반드시, 자기 자신의 싱글턴 인스턴스를 제공하는 getInstance() 를 제공해야 한다.
# 예를 들어, SamlpleClass 클래스일 경우,
# public 으로, SamlpleClass* SamlpleClass::getInstance() 가 있어야 한다.
# 그 후에, char* SamlpleClass::init(int i, char* s) 를 만들어 놓으면,
# 로제타로 생성된 Java에서,
# String SamlpleClass.getInstance().init(10, "test");
# 와 같이 사용할 수 있다.

METHODS = (
	# 코드 구현이 C++ 에 있는 것. Java 코드에서, C++ 코드를 호출.
	'c++	int:Sample.add			; int:a, int:b',
	'c++	void:Sample.printLog	; String:tag, String:log',
	'c++	String:Sample.getString	;',
	'c++	void:Sample.testCallback;',

	# 콜백. 코드 구현이 Java에 있음. (C++ 에서, Java 코드를 호출)
	# 콜백을 사용하기 전에, net.jong10.rosetta.RosettaCallback.initialize() 를 자바에서 호출해줘야 한다.
	'java	void:CallbackSample.showToast	; String:text, int:duration',
)

