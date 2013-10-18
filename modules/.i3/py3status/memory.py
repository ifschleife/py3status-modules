#!/usr/bin/env python

from itertools import islice


class Py3status:

    def show_sys_mem_usage(self, json, i3statuscfg):
        """Shows memory usage as stated by /proc/meminfo"""
        response = {'full_text' : '', 'name' : 'memusage'}

        try:
            with open('/proc/meminfo', 'r') as f:
                memusg = f.readlines()[0:4]
        except IOError:
            memusg = ['0 1', '0 1', '0 1', '0 1']

        # extract numbers
        memusg = [float(m.split()[1]) for m in memusg]

        memavail = memusg[0]
        memfree = memusg[1]
        memused = memavail - memusg[1] - memusg[2] - memusg[3]

        memavail = memavail / 1000
        memused = memused / 1000

        if (memused / memavail) >= 0.6:
            response.update({'color' : i3statuscfg['color_degraded']})
        elif memused / memavail >= 0.9:
            response.update({'color' : i3statuscfg['color_bad']})

        # make human readable
        if memused < 1000:
            memused = "%.0fM" % memused
        else:
            memused = "%.1fG" % (memused/1000)
        if memavail < 1000:
            memavail = "%.0fM" % memavail
        else:
            memavail = "%.1fG" % (memavail/1000)

        response['full_text'] = "MEM: %s / %s" % (memused, memavail)
        return (1, response)


if __name__ == '__main__':
    p = Py3status()
    print(p.show_sys_mem_usage(0, 1))
