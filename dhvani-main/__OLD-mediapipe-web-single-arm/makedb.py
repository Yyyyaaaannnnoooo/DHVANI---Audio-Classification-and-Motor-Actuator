from tinydb import TinyDB, Query

db = TinyDB('db.json')

device_list =   [
					{
						'project':'dhvwani',

						'device1_ip': '192.168.1.10',
						'device2_ip': '192.168.1.11',
						'device1_port': '8888',
						'device2_port': '8887',

						'sound_type_1': "Bell1",
						'speed_limit_max_1': '100',
						'speed_limit_min_1': '50',
						'no_of_notes_1': '8',
						'delay_between_notes_1': '3',
						'accuracy_range_1': '0.95000',



						'sound_type_2': "Bell2",
						'speed_limit_max_2': '100',
						'speed_limit_min_2': '50',
						'no_of_notes_2': '8',
						'delay_between_notes_2': '3',
						'accuracy_range_2': '0.95000',


						'sound_type_3': "Bell3",
						'speed_limit_max_3': '100',
						'speed_limit_min_3': '50',
						'no_of_notes_3': '8',
						'delay_between_notes_3': '3',
						'accuracy_range_3': '0.95000',


						'sound_type_4': "Bell4",
						'speed_limit_max_4': '100',
						'speed_limit_min_4': '50',
						'no_of_notes_4': '8',
						'delay_between_notes_4': '3',
						'accuracy_range_4': '0.95000'

}

				]

for data in device_list:
	db.insert(data)
