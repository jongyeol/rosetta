#ifndef _SAMPLE_H_
#define _SAMPLE_H_

class Sample {
	static Sample* uniqueInstance_;

public:
	Sample();
	static Sample* getInstance();
	int add(int a, int b);
	void printLog(char *tag, char *log);
	char* getString();
	void testCallback();
};

#endif//_SAMPLE_H_
