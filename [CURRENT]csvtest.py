from __future__ import with_statement
from datetime import datetime, timedelta
import subprocess, os, glob, re, __future__
from collections import OrderedDict
import csv


def create_expected_entries(regex_list):
    """
        Function: Creates an expected date-time list for the given function parameters

        Args:
            regex_list: list contains pathname parts of catalog

        Returns:
            the expected date-time entry list for the given function parameters
    """

    days_in_month_dict = {"January": 31, "February": 28,
                          "March": 31, "April": 30,
                          "May": 31, "June": 30,
                          "July": 31, "August": 31,
                          "September": 30, "October": 31,
                          "November": 30, "December": 31}

    options = {1: "January", 2: "February", 3: "March",
               4: "April", 5: "May", 6: "June", 7: "July",
               8: "August", 9: "September", 10: "October",
               11: "November", 12: "December"}

    num_month = {"JAN": 1, "FEB": 2, "MAR": 3,
                 "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7,
                 "AUG": 8, "SEP": 9, "OCT": 10,
                 "NOV": 11, "DEC": 12}

    expected_block_parts = []  # Contains all block parts from regex list
    # no_duplicate_expected_block_parts = []
    main_list_block_parts = []
    dict_name_block_part = OrderedDict()  # OrderedDict maintains order of key:value insertion order
    no_duplicate_main_list_block_parts = []

    for p in regex_list:
        # gets time interval
        start_time, end_time = p[5], p[8]
        int_start_time = int(start_time)
        int_end_time = int(end_time)
        time_difference = int_end_time - int_start_time
        str_time = str(time_difference)
        time_interval_rm_zeros = str_time.replace('00', "")

        # Name of block part
        Apart, Bpart, Cpart, month, Fpart = p[2], p[3], p[4], p[6], p[9]
        name_block_part = Apart + '/' + Bpart + '/' + Cpart + '/' + month + '/' + Fpart
        expected_block_parts.append(name_block_part)  # Just to see a list of the block parts in a list

        block_part_list = [time_interval_rm_zeros, p[6], p[7]]      # [time interval, month, year]
        dict_name_block_part[name_block_part] = block_part_list

        main_list_block_parts.append(dict_name_block_part)

    for x in main_list_block_parts:
        if x not in no_duplicate_main_list_block_parts:
            no_duplicate_main_list_block_parts.append(x)

    # for p in expected_block_parts:
    #     if p not in no_duplicate_expected_block_parts:
    #         no_duplicate_expected_block_parts.append(p)

    # parts_groups = []
    # no_duplicate_parts_groups = []
    block_part_regex = '^(\S+\s*\S*)/(\S+\s*\S+\s*\S*\s*)/(\S*\s*\S*)/(\S+\s*\S*\s*\S*)/(\S+\s*\S*\s*\S*)'
    # for entry in no_duplicate_expected_block_parts:
    #     match = re.search(block_part_regex, entry)
    #     if match is not None:
    #         parts_groups.append(match.groups())

    # for i in parts_groups:
    #     if i not in no_duplicate_parts_groups:
    #         no_duplicate_parts_groups.append(i)

    # for x in no_duplicate_expected_block_parts:
    #     print(x)

    expected_entries = []

    for key, value in no_duplicate_main_list_block_parts[0].items():
        block_part_regex = '^(\S+\s*\S*)/(\S+\s*\S+\s*\S*\s*)/(\S*\s*\S*)/(\S+\s*\S*\s*\S*)/(\S+\s*\S*\s*\S*)'
        match = re.search(block_part_regex, key)
        Apart, Bpart, Cpart, Fpart = match.groups()[0], match.groups()[1], match.groups()[2], match.groups()[4]
        first_half = Apart + '/' + Bpart + '/' + Cpart + '/'
        second_half = '/' + Fpart

        block_time_interval = int(value[0])  # GETS the actual TIME INTERVAL !!!!
        # select_month = value[1]  # variable is the numeric month
        select_month = num_month[no_duplicate_main_list_block_parts[0][key][1]]  # variable is the numeric month
        year = value[2]  # GETS the actual YEAR !!!!
        select_year = '{}'.format(year)
        days_of_selected_month = days_in_month_dict[options[num_month[no_duplicate_main_list_block_parts[0][key][1]]]]

        day = 01  # Starting DAY
        start_hour = "0000"  # Starting HOUR

        #  Create an hour time list that can be iterated/utilized in main while loop BASED ON EA BLOCK PART
        hour_time = [start_hour]
        iteration = 0
        int_new_hour = 0
        while int_new_hour < int("2400"):
            hour_obj = datetime.strptime(hour_time[iteration], "%H%M")
            new_hour_obj = hour_obj + timedelta(hours=block_time_interval)
            string_new_hour = new_hour_obj.strftime("%H%M")
            if string_new_hour == "0000":
                break
            int_new_hour = int(string_new_hour)
            hour_time.append(string_new_hour)
            iteration = iteration + 1
        # print(hour_time) # prints each hour_time list for each EXPECTED BLOCK PART

        #  iterates through each hour time BASED ON THE TIME INTERVAL FOR EACH BLOCK PART ex: main_test3
        while day <= days_of_selected_month:
            for y in range(len(hour_time)):
                begin_date = "{}{}{}:{}".format(day, select_month, select_year, hour_time[y])
                date_obj = datetime.strptime(begin_date, "%d%m%Y:%H%M")  # formats into time object
                end_time = date_obj + timedelta(hours=0)  # increments time delta to time object
                format_date = end_time.strftime("%d%b%Y:%H%M")  # reformats back to string correct format
                upper_format_date = format_date.upper()  # finalizes uppercase format
                first_time_window = upper_format_date  # setting to a time window variable to be used

                # at i = 3, once it gets here it will go to end time and add 1800 with 0600 hours,
                # incrementing to 02Jan
                end_time = "{}{}{}:{}".format(day, select_month, select_year, hour_time[y])
                date_obj = datetime.strptime(end_time, "%d%m%Y:%H%M")
                end_time = date_obj + timedelta(hours=block_time_interval)
                second_format_date = end_time.strftime("%d%b%Y:%H%M")
                second_upper_format_date = second_format_date.upper()

                # gets the 1200 in 01Jan2017:1200
                dss_catalog_regex = '(\d{4})$'
                match_time_interval = re.search(dss_catalog_regex, second_upper_format_date)
                list = []
                list.append(match_time_interval.groups())

                for ele in list[0]:
                    if ele == "0000":
                        midnight = "2300"
                        end_time = "{}{}{}:{}".format(day, select_month, select_year, midnight)
                        date_obj = datetime.strptime(end_time, "%d%m%Y:%H%M")
                        second_format_date = date_obj.strftime("%d%b%Y:%H%M")
                        second_upper_format_date = second_format_date.upper().replace("2300", "2400")

                second_time_window = second_upper_format_date
                time_window_string = '{}{}{}{}{}'.format(first_half, first_time_window, '/', second_time_window,
                                                         second_half)
                # expected_entries.append(time_window_string)
                # print time_window_string
                expected_entries.append(time_window_string)

            day = day + 1

    return expected_entries

# def create_csv_format(expected, actual):
#     # availability = {'MISSING: ': 'm', 'available': 'a'}
#     comma = ','
#     csv_list = []
#     new_master_block_part_regex_timeblock_combined = '^(\S+\s*\S*\s*\S*/\S+\s*\S*\s*\S*/\S+\s*\S*\s*\S*/)(\d+\S+\d+:\d+\d+\S+\d+:\d+)/(\S+\s*\S*)'
#
#     for t in expected[0:10]:
#         match = re.search(new_master_block_part_regex_timeblock_combined, t)
#         if t not in actual:
#             combined = match.groups()[0] + match.groups()[2]
#             time_block = match.groups()[1]
#             missing = 'm'
#             final_string = ''.join([combined, comma, missing, comma, time_block])
#             csv_list.append(final_string)
#             print(final_string)
#
#         else:
#             combined = match.groups()[0] + match.groups()[2]
#             time_block = match.groups()[1]
#             avail = 'a'
#             final_string = ''.join([combined, comma, avail, comma, time_block])
#             csv_list.append(final_string)
#             print(final_string)
#
#     return csv_list


def create_csv_format(master):
    csv_list = ['blockname,availability,timeblock']
    comma = ','
    separate = '/'
    fart_regex = '^(\S+ )?(\S+\s?/\S+\s?\S*\s?\S*/\S+\s?\S?/)(\d+\S+\d+:\d+)/(\d+\S+\d+:\d+)/(\S+\s?\S?)'
    for x in master:
        match_actual_parts = re.search(fart_regex, x)
        if match_actual_parts.groups()[0] == 'MISSING: ':
            combined = ''.join([match_actual_parts.groups()[1], match_actual_parts.groups()[4]])
            time_block = ''.join([match_actual_parts.groups()[2], separate, match_actual_parts.groups()[3]])
            missing = 'm'
            final_string = ''.join([combined, comma, missing, comma, time_block])
            csv_list.append(final_string)
            # print(final_string)

        else:
            combined = ''.join([match_actual_parts.groups()[1], match_actual_parts.groups()[4]])
            time_block = ''.join([match_actual_parts.groups()[2], separate, match_actual_parts.groups()[3]])
            missing = 'a'
            final_string = ''.join([combined, comma, missing, comma, time_block])
            csv_list.append(final_string)

    return csv_list


def regex(the_file):
    """
        Function: Obtains time-series data path names with date-times.
                  Scans for

        Args:
            the_file: Takes dss catalog file to obtain date-time from time series data

        Returns:
            Should return a full list that contains missing date-time entries from both expected entries
            and the catalog entries from a given dss catalog file

    """
    for i in the_file:
        infile = i
        with open(infile, 'r') as my_file:
            line_entries = my_file.read().splitlines()

        print ("----------------------------------")

        # Obtains all pathname parts
        # From '1  T23       Undefi  01JAN17 15:37  GAT   2 9999   /SHG/MARFC/PRECIP/01JAN2017:1200/01JAN2017:1800/QPF-QPF/'
        pathname_parts_regex = '^\s*([0-9]+)\s+(T[0-9]+)\s+.*\s+/([a-zA-Z]+)/(\S*\s*\S*\s*\S*)/([a-zA-Z]+)/\d{2}\w{3,}\d{4,}:(\d{3,})/\d{2}(\w{3,})(\d{4,}):(\d{3,})/(\S+)/'
        parts = []

        for part_entry in line_entries:
            match_parts = re.search(pathname_parts_regex, part_entry)
            if match_parts is not None:
                parts.append(match_parts.groups())
                # print(match_parts.groups())
        # prints: ('3864', 'T2967', 'SHG', 'UPPER SUSQUEHANNA RIVER', 'PRECIP', '1800', 'JAN', '2017', '2400', 'WPC-QPF')

        # # TODO: get actual list of entries for time series data
        regex_actual_parts = '^\s*([0-9]+)\s+(T[0-9]+)\s+.*\s+/(\S*/\S*\s*\S*\s*\S*/\S*/\S*/\S*/\S*)/$'
        actual_parts = []
        for actual_part_entry in line_entries:
            match_actual_parts = re.search(regex_actual_parts, actual_part_entry)
            if match_actual_parts is not None:
                actual_parts.append(match_actual_parts.group(3))

        # CONSISTS OF THE EXPECTED ENTRIES FOR CATALOG DATA
        the_expected_entries = create_expected_entries(regex_list=parts)

        master_data = []
        for t in the_expected_entries:
            if t not in actual_parts:
                missing_part = "{}{}".format('MISSING: ', t)
                master_data.append(missing_part)
            else:
                master_data.append(t)

        # CONSISTS OF CSV FORMAT
        csv_format_master_entries = create_csv_format(master=master_data)

        # TODO FIX TO ACCEPT ALL/NEW CSV FILES
        f = open('final2.csv', 'wb')
        for line in csv_format_master_entries:
            f.write('{}{}'.format(line, '\n'))  # Give your csv text here.
        f.close()

########################################################################################################################
dssTxtList = []

# TODO add all catalog files to list
# Reads and obtains DSS catalogs and adds catalog file name into List
# for files in glob.glob("*.txt"):
for files in glob.glob("precip.2017.01.dsc.txt"):
    dssTxtList.append(files)


# Performs regex on .dsc files to obtain start date/time and end date/time of data
regex(dssTxtList)
