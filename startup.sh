APP_NAME="PSICalc-Viewer.app" 
DMG_NAME="PSICalc-Viewer.dmg"
DEVELOPER_CERT="Developer ID Application: Joeeph Deweese (AYX28QCD98)"
APP_SPECIFIC_PASSWORD="xbll-agln-iafc-chsh"
USER_EMAIL="jdeweeselab@gmail.com"
fbs clean
fbs freeze

echo "*** Code Signing Executables ***"

echo "*** LEVEL ONE ***"
FILES=$(find target/$APP_NAME/Contents/MacOS/* -depth)
for LIB in $FILES
do
  codesign -s  "$DEVELOPER_CERT" \
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
  codesign -s "$DEVELOPER_CERT" \
  --entitlements entitlements.plist \
  --verbose -o runtime \
  --preserve-metadata=identifier,entitlements,requirements,runtime \
  --timestamp $LIB
done

codesign -s "$DEVELOPER_CERT" \
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
codesign -s "$DEVELOPER_CERT" \
--entitlements entitlements.plist \
--verbose -o runtime \
--preserve-metadata=identifier,entitlements,requirements,runtime \
--timestamp ./target/$DMG_NAME

xcrun altool --notarize-app --verbose --primary-bundle-id "com.jdeweeselab.pcviewer" \
--username "$USER_EMAIL" --password "$APP_SPECIFIC_PASSWORD" \
--file ./target/$DMG_NAME

sleep 900
cd target || exit
xcrun stapler staple "PSICalc-Viewer.app"
xcrun stapler staple "PSICalc-Viewer.dmg"
