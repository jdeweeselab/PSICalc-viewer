APP_NAME="PSICalc-Viewer.app" 
DMG_NAME="PSICalc-Viewer.dmg"
fbs clean
fbs freeze

echo "*** Code Signing Executables ***"

echo "*** LEVEL ONE ***"
FILES=$(find target/$APP_NAME/Contents/MacOS/* -depth)
for LIB in $FILES
do
  codesign -s "Developer ID Application: Thomas Townsley (3746QNA6LZ)" \
  --entitlements entitlements.plist \
  --verbose -o runtime \
  --preserve-metadata=identifier,entitlements,requirements,runtime \
  --timestamp $LIB
done
#--entitlements entitlements.plist \
#--entitlements entitlements.plist \
echo "*** LEVEL TWO ***"
LIBS=$(find target/$APP_NAME/Contents/Resources/lib/* -depth)
for LIB in $LIBS
do
  codesign -s "Developer ID Application: Thomas Townsley (3746QNA6LZ)" \
  --entitlements entitlements.plist \
  --verbose -o runtime \
  --preserve-metadata=identifier,entitlements,requirements,runtime \
  --timestamp $LIB
done

codesign -s "Developer ID Application: Thomas Townsley (3746QNA6LZ)" \
--entitlements entitlements.plist \
--verbose -o runtime \
--preserve-metadata=identifier,entitlements,requirements,runtime \
--timestamp ./target/$APP_NAME

echo "*** Running Tests ***"
# Verify the codesigned application can run on the system
codesign --verify --verbose=4 ./target/$APP_NAME

echo "*** BUILDING DMG ***"
fbs installer

sleep 10

echo "*** Code Signing DMG ***"
codesign -s "Developer ID Application: Thomas Townsley (3746QNA6LZ)" \
--entitlements entitlements.plist \
--verbose -o runtime \
--preserve-metadata=identifier,entitlements,requirements,runtime \
--timestamp ./target/$DMG_NAME

xcrun altool --notarize-app --verbose --primary-bundle-id "com.thomastownsley.pcviewer" \
--username "thomas@mandosoft.dev" --password "@keychain:AC_PASSWORD" \
--file ./target/$DMG_NAME

#xcrun stapler staple "PSICalc-Viewer.app"
#xcrun stapler staple "PSICalc-Viewer.dmg"
