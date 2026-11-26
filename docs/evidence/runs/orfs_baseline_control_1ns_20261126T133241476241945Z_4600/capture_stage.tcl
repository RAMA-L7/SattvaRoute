# Visual capture only: load an existing saved database, no flow stage is invoked.
set db $::env(CAPTURE_DB)
set sdc $::env(CAPTURE_SDC)
read_db $db
read_sdc $sdc
puts "CAPTURE_DB_LOADED $db"
puts "CAPTURE_SDC_LOADED $sdc"
