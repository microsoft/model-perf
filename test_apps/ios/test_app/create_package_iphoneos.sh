# Running the script in the same directory of this script
# Running the script after running build_iphoneos.sh

project_name="test_app"
scheme_name="test_app"
build_dir=`readlink -f build.ios`
build_configuration="Debug"
export_options_plist_path=`readlink -f ./export.plist`
export_archive_path="$build_dir/$project_name.xcarchive"
export_ipa_path="$build_dir/$project_name.ipa"

echo "project_name=${project_name}"
echo "scheme_name=${scheme_name}"
echo "build_dir=${build_dir}"
echo "build_configuration=${build_configuration}"
echo "export_options_plist_path=${export_options_plist_path}"
echo "export_archive_path=${export_archive_path}"
echo "export_ipa_path=${export_ipa_path}"

cd ${build_dir}
# Clean
xcodebuild clean -project ${project_name}.xcodeproj \
                 -sdk iphoneos \
                 -scheme ${scheme_name} \
                 -configuration ${build_configuration}

# Archive
xcodebuild archive -project ${project_name}.xcodeproj \
                   -scheme ${scheme_name} \
                   -configuration ${build_configuration} \
                   -archivePath ${export_archive_path} \
                   -allowProvisioningUpdates

# Create ipa
xcodebuild  -exportArchive \
            -archivePath ${export_archive_path} \
            -exportPath ${export_ipa_path} \
            -exportOptionsPlist ${export_options_plist_path} \
            -allowProvisioningUpdates

exit
