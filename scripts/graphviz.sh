# Copy files into Resources folder
RES=src/main/resources/base/lib/
	
cp /usr/local/bin/dot $RES
cp -r /usr/local/lib/graphviz $RES

cp /usr/local/opt/libtool/lib/libltdl.7.dylib $RES
cp /usr/local/lib/libgvc.6.dylib $RES
cp /usr/local/lib/libxdot.4.dylib $RES
cp /usr/local/lib/libcgraph.6.dylib $RES
cp /usr/local/lib/libpathplan.4.dylib $RES
cp /usr/local/lib/libcdt.5.dylib $RES

