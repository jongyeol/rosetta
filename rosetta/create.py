#!/usr/bin/python
# -*- coding: utf-8 -*-

# Rosetta : A simple JNI wrapper generator for Android.
# http://bitbucket.org/jong10/rosetta
# coded by Jong10 <jong10@gmail.com>

# Usage
"""
Android Project Path> .rosetta/create.py <C++ JNI Path> <Java Path>
"""

import sys, re, os
import settings

STR_PREFIX = 'str_'

#	Java Type	C++ Type
TYPES = {
	# key		[0]				[1]					[2]		[3]						[4]
	'boolean':	('jboolean',	'unsigned char',	'Z',	'CallBooleanMethod',	'Boolean'),
	'byte':		('jbyte',		'char',				'B',	'CallByteMethod',		'Byte'),
	'char':		('jchar',		'unsigned short',	'C',	'CallCharMethod',		'Character'),
	'short':	('jshort',		'short',			'S',	'CallShortMethod',		'Short'),
	'int':		('jint',		'int',				'I',	'CallIntMethod',		'Integer'),
	'long':		('jlong',		'long',				'J',	'CallLongMethod',		'Long'),
	'float':	('jfloat',		'float',			'F',	'CallFloatMethod',		'Float'),
	'double':	('jdouble',		'double',			'D',	'CallDoubleMethod',		'Double'),
	'void':		('void',		'void',				'V',	'CallVoidMethod',		'Void'),
	
	'String':	('jstring',		'char*','Ljava/lang/String;', 'CallObjectMethod', 'String'),
	
	# TODO: Array is.. not yet. :-(
}


# if not valid regular expression, then to die.
def valid_or_die(s, regexp):
	p = re.compile(regexp, re.VERBOSE)
	if p.match(s):
		return True
	else:
		print '[Error!!] Regexp not accepted!!'
		print '`' + s + '`'
		sys.exit(2)


# merge path from path and file
def gen_path(path, file):
	fullpath = path
	if path[-1] != os.sep:
		fullpath += os.sep
	return fullpath + file


# Variable
class Var():
	def __init__(self, type, var_name):
		self.type = str(type)
		self.name = str(var_name)
		pass
	
	def __str__(self):
		return self.type + ':' + self.name
	
	# Java용으로 이름을 변환하자.
	def java_type(self):
		return self.type
	
	# C++로 된 JNI 타입이름을 돌려준다.
	def cpp_type(self):
		return TYPES[self.type][0]

	# C++에서 native 타입으로 돌려준다.
	def native_type(self):
		return TYPES[self.type][1]

	# Java Class Type (primitive 타입 대신 Class로 된 것)
	def class_type(self):
		return TYPES[self.type][4]
	
	# C++로 된 변수이름을 캐스팅해서 돌려준다.
	def cpp_name(self):
		results = '(' + self.native_type() + ')'
		if self.type == 'String':
			results += STR_PREFIX
		results += self.name
		return results

	# Signature
	def signature(self):
		return TYPES[self.type][2]
	
	# java method type
	def method_type(self):
		return TYPES[self.type][3]

# 메소드 하나
class Method():
	# 입력된 한 줄을 파싱해서 메소드 객체를 설정한다.
	def __init__(self, line):
		self.parse(line)
	
	# 한 줄을 파싱한다.
	def parse(self, line):
		PATTERN = r'''
			^
			\s*
			(c\+\+|java)	# 언어 종류
			\s*
			(\w+)			# 리턴 타입
			:
			([\w]+)			# 클래스
			\.
			([\w]+)			# 메소드
			\s*
			;
			\s*
			(.*)			# 매개변수들..
			$
		'''
		
		valid_or_die(line, PATTERN)
		
		# 정규식 컴파일
		p = re.compile(PATTERN, re.VERBOSE)
		
		# 언어, 리턴, 클래스이름, 메소드, 매개변수들..
		self.lang, self.ret, self.clazz, self.method, arguments = p.match(line).groups()
		
		# 매개변수를 파싱한다.
		self.args = []
		for t in arguments.split(','):
			p = re.compile(r'\s*(\w+):(\w+)\s*')
			results = p.match(t)
			if results:
				type = results.groups()[0]
				var_name = results.groups()[1]
				self.args.append(Var(type, var_name))
	
	# C++용 함수 이름을 만든다.
	def cpp_func(self):
		return 'Java_%s_%s_%s' % (settings.PACKAGE.replace('.', '_'), self.clazz, self.method)
	
	# C++용 매개변수 목록을 만든다.
	def cpp_args(self):
		return ''.join(
			", %s %s" % (arg.cpp_type(), arg.name)
			for arg in self.args
		)
	
	# Java용 매개변수 목록
	def java_args(self):
		return ', '.join('%s %s' % (a.type, a.name) for a in self.args)
	
	# C++용 코드의 본문을 만든다.
	def cpp_body(self):
		def append_line(code):
			self.codes += ''.join('\t' for i in range(self.indent)) + str(code) + '\n'
		
		def generate_invoke(ret):
			results = ''
			# 리턴값
			if ret:
				results += ret.name + ' = '
			# 호출부
			results += 'singleton->%s(' % self.method
			results += ', '.join(
				a.cpp_name() for a in self.args
			)
			results += ');'
			return results
		
		
		self.codes = ''
		self.indent = 1
		ret_var = None
		string_list = [a for a in self.args if a.type == 'String']
		
		# 리턴할 변수가 있는지 확인하고..
		if self.ret != 'void':
			ret_var = Var(self.ret, 'ret')
			append_line('%s %s;' % (ret_var.native_type(), ret_var.name))
		
		
		# 문자열 할당
		for v in string_list:
			append_line('const char* %s = env->GetStringUTFChars(%s, 0);' % (STR_PREFIX + v.name, v.name))
		
		# 싱글턴 인스턴스 가져옴
		append_line('%s* singleton = %s::getInstance();' % (self.clazz, self.clazz))
		
		# 리턴값 = 실제 메소드 호출
		append_line(generate_invoke(ret_var))
		
		# 문자열 릴리즈
		for v in string_list:
			append_line('env->ReleaseStringUTFChars(%s, %s);' % (v.name, STR_PREFIX + v.name))
		
		# 리턴
		if ret_var:
			return_variable = ret_var.name
			
			# 만약, 문자열 리턴이면,
			if ret_var.type == 'String':
				append_line('jstring str_ret = env->NewStringUTF(ret);')
				return_variable = 'str_ret'
			
			# 리턴할 변수 이름.
			append_line('return %s;' % return_variable)
		
		return self.codes
	
	
	# C++ native용 리턴타입을 돌려준다.
	def native_ret_type(self):
		return TYPES[self.ret][1]
	
	
	# 이 메소드 객체에 대한 C++ 코드를 생성한다.
	def cpp_code(self):
		results = ''
		results += """
JNIEXPORT %s JNICALL
%s(JNIEnv *env, jclass clazz%s)
{
%s}
""" % (
			Var(self.ret, '').cpp_type(),
			self.cpp_func(),
			self.cpp_args(),
			self.cpp_body()
		)
		return results
	
	# 이 메소드 객체에 대한 Java 코드를 생성한다.
	# public native <리턴> <메소드이름>(<매개변수타입> <매개변수이름> ...);
	def java_code(self):
		return '\tpublic native %(ret)s %(method)s(%(args)s);' % {
					'ret': self.ret,
					'method': self.method,
					'args': self.java_args()
				}
	
	# 콜백용 args를 만든다.
	def callback_args(self):
		return ', '.join(
			"%s %s" % (arg.native_type(), arg.name)
			for arg in self.args
		)
	
	# 콜백용 body를 만든다.
	def callback_body(self):
		if len(self.args) > 0:
			args = ', ' + ', '.join(
				'(' + arg.cpp_type() + ')' + ( (arg.type == 'String') and STR_PREFIX or '' ) + arg.name
				for arg in self.args
			)
		else:
			args = ''
		
		codes = '''// get Class
jclass clazz = jenv->FindClass("%(class)s");
assert(clazz);

jmethodID smid = jenv->GetStaticMethodID(clazz, "getInstance", "()L%(class)s;");
assert(smid);

// get instance
jobject obj = jenv->CallStaticObjectMethod(clazz, smid);
assert(obj);

// get instance method
jmethodID mid = jenv->GetMethodID(clazz, "%(method)s", "%(signatures)s");
assert(mid);\n\n''' % {
			'class': (settings.PACKAGE + '.' + self.clazz).replace('.', '/'),
			# TODO: -_-;;
			'method': self.method,
			'signatures': self.signatures(),
		}
		
		## 문자열 할당
		for v in self.args:
			if v.type == 'String':
				codes += 'jstring %s = createJStringFrom(%s, "ksc-5601");\n' % (STR_PREFIX + v.name, v.name)
		
		ret_var = Var(self.ret, 'ret')
		
		codes += '// Call java method\n'
		# 메소드 호출
		if self.ret != 'void':
			codes += '%(type)s ret = (%(type)s)' % {'type': ret_var.cpp_type()}
		
		codes += 'jenv->%(method_type)s(obj, mid%(args)s);\n' % {
			'method_type': ret_var.method_type(),
			'args': args,
		}

		# 로컬 변수들 릴리즈
		codes += '''
jenv->DeleteLocalRef(clazz);
jenv->DeleteLocalRef(obj);'''
		## 문자열 릴리즈
		for v in self.args:
			if v.type == 'String':
				codes += 'jenv->DeleteLocalRef(%s);' % (STR_PREFIX + v.name)
		
		# 리턴이 문자열일 경우?
		if self.ret == 'String':
			codes += '''
// return string
if (ret) {
	return convertEncode(&ret, "ksc-5601");
}
else {
	return NULL;
}'''
		# 리턴
		elif self.ret != 'void':
			codes += '''
// return
return (%s)ret;''' % ret_var.native_type()
		
		return '\n'.join('\t\t' + line for line in codes.split('\n'))
	
	# 현재 메소드의 JNI 시그니쳐를 만든다.
	def signatures(self):
		return '(%(args)s)%(ret)s' % {
			'args': ''.join(arg.signature() for arg in self.args),
			'ret': Var(self.ret, '').signature()
		}
	
	# 콜백용 C++ 코드를 만든다.
	def callback_cpp_code(self):
		codes = '''
\t%(ret_type)s Callback_%(class)s_%(method)s(%(args)s)
\t{
%(body)s
\t}''' % {
			'ret_type': self.native_ret_type(),
			'package': settings.PACKAGE.replace('.', '_'),
			'class': self.clazz,
			'method': self.method,
			'args': self.callback_args(),
			'body': self.callback_body()
		}
		return codes

	# 콜백용 C++ 헤더코드를 만든다.
	def callback_hpp_code(self):
		codes = '%(ret_type)s Callback_%(class)s_%(method)s(%(args)s);' % {
			'ret_type': self.native_ret_type(),
			'package': settings.PACKAGE.replace('.', '_'),
			'class': self.clazz,
			'method': self.method,
			'args': self.callback_args()
		}
		return codes


# 파일에서, 메소드 목록을 가져온다.
def input_from_settings():
	# 저장해야 되는 줄인지 체크한다.
	def is_valid(line):
		if len(line) > 0 and line[0] != '#':
			return True
		else:
			return False
	
	# 파일을 열어서, 각 줄을 읽어서 파싱한다.
	methods = []
	for line in settings.METHODS:
		a_line = line.strip()
		if is_valid(a_line):
			methods.append(Method(a_line))
	
	return methods


# C++ 코드를 생성한다.
def generate_cpp(methods):
	codes = ''
	
	# 헤더파일
	codes += ''.join('#include <' + f + '>\n' for f in settings.STD_INCLUDE_FILES) + '\n'
	codes += ''.join('#include "' + f + '"\n' for f in settings.USR_INCLUDE_FILES) + '\n'
	
	# extern "C"
	codes += 'extern "C" {\n'
	
	# 메소드를 하나씩 출력한다.
	for m in methods:
		codes += m.cpp_code() + '\n'
	
	# close extern "C"
	codes += '}\n'

	return codes


# 콜백 C++ 코드를 생성한다.
def generate_callback_cpp(methods):
	CODE_HEAD = '''// callback methods
#include <jni.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

JNIEnv* jenv = NULL;

extern "C" {
	JNIEXPORT void JNICALL
	Java_%(init_class)s_initialize(JNIEnv* env, jclass clazz)
	{
		jenv = env;
	}
	
	char* convertEncode(jstring* pStr, const char* encode) {
		jclass clazz = jenv->FindClass("java/lang/String");
		jmethodID mid = jenv->GetMethodID(clazz, "getBytes", "(Ljava/lang/String;)[B");
		jbyteArray arr = (_jbyteArray*)jenv->CallObjectMethod(*pStr, mid, jenv->NewStringUTF(encode));
		int len = jenv->GetArrayLength(arr);
		jbyte* bytes = jenv->GetByteArrayElements(arr, 0);
		char* ret = (char*)malloc(len + 1);
		strncpy(ret, (char*)bytes, len);
		ret[len] = 0;
		jenv->ReleaseByteArrayElements(arr, bytes, JNI_ABORT);
		jenv->DeleteLocalRef(arr);
		jenv->DeleteLocalRef(clazz);
		return ret;
	}
	 
	jstring createJStringFrom(char* data, const char* encoding) {
		jbyteArray javaBytes;
		int len = strlen( data );
		javaBytes = jenv->NewByteArray(len);
		jenv->SetByteArrayRegion(javaBytes, 0, len, (jbyte *)data );
		jstring str;
		jclass cls = jenv->FindClass("java/lang/String");
		jmethodID mid_newString = jenv->GetMethodID(cls, "<init>", "([BLjava/lang/String;)V");
		str = (jstring)jenv->NewObject(cls, mid_newString, javaBytes, jenv->NewStringUTF(encoding) );
		jenv->DeleteLocalRef(javaBytes);
		jenv->DeleteLocalRef(cls);
		return str;
	}
''' % {'init_class': settings.PACKAGE.replace('.', '_') + '_' + settings.CALLBACK_CLASS}
	
	codes = ''
	codes += CODE_HEAD
	codes += '\n'.join(m.callback_cpp_code() for m in methods)
	codes += '\n}\n'
	
	return codes

# 콜백 C++ 헤더코드를 생성한다.
def generate_callback_hpp(methods):
	CODE_HEAD = '''#ifndef _%(callback_header)s
#define _%(callback_header)s

extern "C" {
''' % {'callback_header': settings.CALLBACK_HEADER_FILENAME.replace('.', '_').upper()}

	codes = ''
	codes += CODE_HEAD
	codes += '\n'.join('\t' + m.callback_hpp_code() for m in methods)
	codes += '\n}\n\n#endif\n'
	return codes


"""
package settings.PACKAGE;
public class <클래스이름> {
	private static <클래스이름> uniqueInstance = new <클래스이름>();
	private <클래스이름>() {
	}
	public static <클래스이름> getInstance() {
		return uniqueInstance;
	}
	public native <리턴> <메소드이름>(<매개변수타입> <매개변수이름> ...);
	
	...(생략)...
	
	static {
		System.loadLibrary("<라이브러리이름>");
	}
}
"""
# 클래스 하나에 해당하는 Java 코드를 생성한다.
def generate_java(clazz, methods):
	CODE_HEAD = """package %(package)s;
public class %(class)s {
	private static %(class)s uniqueInstance = new %(class)s();
	private %(class)s() {
	}
	public static %(class)s getInstance() {
		return uniqueInstance;
	}
""" % {'package': settings.PACKAGE, 'class': clazz}
	
	CODE_TAIL = """
	static {
		System.loadLibrary(\"%(lib_name)s\");
	}
}
"""	% {'lib_name': settings.LIB_NAME}
	
	codes = ''
	codes += CODE_HEAD
	codes += '\n'.join(m.java_code() for m in methods)
	codes += CODE_TAIL
	codes += '\n'
	
	return codes


# {클래스이름: 내용, 클래스이름: 내용 ... }으로 변환해서 리턴한다.
# 섞여있는 메소드 정의를 클래스별로 묶어준다.
def split_java(methods):
	group = {}
	for m in methods:
		if not group.has_key(m.clazz):
			group[m.clazz] = [m]
		else:
			group[m.clazz].append(m)
	return group


# 해당 파일이 들어갈 디렉토리를 상위디렉토리부터 모두 생성한다.
def makedir(path_list):
	path = ''
	for p in path_list:
		path += p + os.sep
		if path[:-1] != "" and not os.path.isdir(path[:-1]):
			os.mkdir(path[:-1])


# 해당 파일을 열어서, 내용을 쓴다.
def write_to_file(file, str):
	makedir(file.split(os.sep)[:-1])
	f = open(file, 'w')
	f.write(str)
	f.close()
	
	print 'created: ' + file
	
	# 디버깅용
	#print '*******************************************************'
	#print '***** %s' % file
	#print '*******************************************************\n'
	#print str


# Java에서 C++을 호출하기 위한, 스텁코드 생성
def JavaToCpp(methods, cpp_path, java_path):
	# `Rosetta.cpp`에 C++ 코드를 출력한다.
	cpp_codes = generate_cpp(methods)
	cpp_file = gen_path(cpp_path, settings.CPP_FILENAME)
	write_to_file(cpp_file, cpp_codes)
	
	# 클래스별로 Java 코드를 출력한다.
	for clazz, java_methods in split_java(methods).items():
		path = gen_path(java_path, settings.PACKAGE.replace('.', os.sep))
		filename = gen_path(path, clazz + '.java')
		write_to_file(filename, generate_java(clazz, java_methods))


# C++에서 Java를 호출하기 위한, 스텁코드 생성
def CppToJava(methods, cpp_path):
	# `Callback.cpp`에 C++ 코드를 출력한다.
	codes = generate_callback_cpp(methods)
	file = gen_path(cpp_path, settings.CALLBACK_FILENAME)
	write_to_file(file, codes)
	
	# `Callback.h`에 C++ 코드헤더를 출력한다.
	codes = generate_callback_hpp(methods)
	file = gen_path(cpp_path, settings.CALLBACK_HEADER_FILENAME)
	write_to_file(file, codes)


# main function
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: rosetta/create.py <C++ Path> <Java Path>'
		print '   ex) rosetta/create.py jni gen'
		sys.exit(1)
	
	cpp_path = sys.argv[1]
	java_path = sys.argv[2]
	
	# 파일에서 입력을 받는다.
	methods = input_from_settings()
	
	# 메소드를 분류한다.
	cpp_methods = [m for m in methods if m.lang == 'c++']
	java_methods = [m for m in methods if m.lang == 'java']
	
	# Java에서 C++을 호출하기 위한, 스텁코드 생성
	JavaToCpp(cpp_methods, cpp_path, java_path)
	
	# C++에서 Java를 호출하기 위한, 스텁코드 생성
	CppToJava(java_methods, cpp_path)


