SELECT     pickup_local_time, 
           pickup_utc_time, 
           cancel_fee_local, 
           cancel_fee_local, 
           city_id, 
           rider_app, 
           rider_device, 
           rider_trip_count, 
           bills.rider_id AS rider_id,
           (LENGTH(vehicle_ids) - LENGTH(REPLACE(vehicle_ids, ',', '')) + 1) AS partner_vehicle_count,
           driver_trip_count, 
           drivers.driver_id, 
           dropoff_local_time, 
           dropoff_utc_time, 
           esttime_to_pickup, 
           trips.request_type, 
           trips.entered_destination, 
           paid_cash, 
           bills.completed_trip, 
           bills.surged_trip, 
           trip_fare_local, 
           trip_fare_usd, 
           partner_id, 
           request_local_time, 
           request_utc_time, 
           distance_to_pickup, 
           time_to_pickup, 
           trip_status, 
           trip_distance_miles, 
           trip_duration_seconds, 
           trips.trip_id, 
           vehicle_trip_count, 
           trips.vehicle_id, 
           vehicle_type, 
           pickup_geo, 
           dropoff_geo 
FROM       trips 
INNER JOIN bills 
ON         bills.trip_id = trips.trip_id 
INNER JOIN riders 
ON         riders.rider_id = bills.rider_id 
INNER JOIN drivers 
ON         drivers.driver_id = bills.driver_id
INNER JOIN drivers AS partners
ON         driver_id = bills.partner_id
INNER JOIN vehicles 
ON         vehicles.vehicle_id = trips.vehicle_id
WHERE      city_id = 1