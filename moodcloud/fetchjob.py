import sys
import urllib
import time, datetime

LIMIT = 60
THRESHOLD = 5

start = datetime.datetime.utcnow()
print "Starting at: %s" % start

call_time_sum = 0.0
call_time_count = 0.0

for i in range(12):
    before = datetime.datetime.utcnow()
    print "\tRunning: %s" % before
    response = urllib.urlopen('http://moodcloud.azurewebsites.net/data/')
    html = response.read()
    print html
    after = datetime.datetime.utcnow() - before
    call_time_sum += after.microseconds
    call_time_count += 1.0
    call_time_avg = (call_time_sum / call_time_count) / 1000000
    print "\t\tAverage Call Time: %f" % call_time_avg
    duration = datetime.datetime.utcnow() - start
    if duration.seconds + max(THRESHOLD, call_time_avg) > LIMIT:
        break
    diff = THRESHOLD - after.seconds
    if diff > 0:
        print "\t\tSleeping for: %d" % diff
        time.sleep(diff)

end = datetime.datetime.utcnow()
print "Ending at: %s" % end
diff = end-start
print "Duration: %d" % diff.seconds
