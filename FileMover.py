import os
from os import path
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from re import search
from re import findall
import shutil
import json
import magic

class FileMover:
	FILE_BASE = os.path.dirname(os.path.abspath(__file__)) + '\\Sources\\Files\\'
	destination_path = ''
	location_path = ''

	def __init__(self):
		window = Tk()
		window.title("File Path Declarations")
		window.eval('tk::PlaceWindow . center')
		IMAGE_BASE = os.path.dirname(os.path.abspath(__file__)) + '\\Sources\\Images\\'
		window.iconbitmap('{}BlackIcon.ico'.format(IMAGE_BASE))

		# Create input labels.
		Label(window, text = "File Extension").grid(row = 1, column = 1, sticky = W)
		Label(window, text = "Location Path").grid(row = 2, column = 1, sticky = W)
		Label(window, text = "Destination Path").grid(row = 3, column = 1, sticky = W)

		# Take file extension input.
		self.file_extension = StringVar()
		Entry(window, textvariable = self.file_extension, justify = RIGHT).grid(row = 1, column = 2)

		# Take file path inputs.
		bt_base_path = Button(window, text = "Browse...", command = self.set_location_path).grid(row = 2, column = 2, sticky = E)
		bt_destination_path = Button(window, text = "Browse...", command = self.set_destination_path).grid(row = 3, column = 2, sticky = E)

		# Path action buttons
		bt_submit_paths = Button(window, text = "Set Path", command = self.set_path).grid(row = 1, column = 4, sticky = E)
		bt_delete_paths = Button(window, text = "Delete Path", command = self.delete_path).grid(row = 2, column = 4, sticky = E)
		bt_show_paths = Button(window, text = "Show Paths", command = self.get_paths).grid(row = 3, column = 4, sticky = E)

		# Exit window and run the File Mover
		bt_run_mover = Button(window, text = "Run File Mover", command = self.move_files).grid(row = 4, column = 4, sticky = E)

		# Create an event loop and add closing protocol
		window.mainloop()

	def set_location_path(self):
		try:
			FileMover.location_path = filedialog.askdirectory(mustexist=1, initialdir=os.getcwd(), title='Please select the directory you wish {} files to be moved from'.format(self.file_extension.get())).replace("/","\\")
		except Exception as exception:
			messagebox.showerror("Set Base Path Error:", exception)
			return

	def set_destination_path(self):
		try:
			FileMover.destination_path = filedialog.askdirectory(mustexist=1, initialdir=os.getcwd(), title='Please select the directory you wish {} files to go to'.format(self.file_extension.get())).replace("/","\\")
		except Exception as exception:
			messagebox.showerror("Set Destination Path Error:", exception)
			return

	def get_paths(self):
		try:
			pathlist = []
			with open('{}Paths.JSON'.format(FileMover.FILE_BASE)) as handle:
				json_path_object = json.load(handle)
			for element in json_path_object['path_object']:
				pathlist.append(element['file_extension'] + ' files are being sent from ' + element['location_path'] + ' to ' + element['destination_path'])
			messagebox.showinfo("Registered Paths:", '\n\n'.join(map(str, pathlist)))
			return
		except ValueError: # Fills the JSON object with a default path when no other paths exist
			json_path_object = {}
			json_path_object['path_object'] = []
			json_path_object['path_object'].append({
			'file_extension' : 'extension',
			'location_path' : 'current location',
			'destination_path' : 'destination location'
			})
			with open('{}Paths.JSON'.format(FILE_BASE), 'w') as handle:
				json.dump(json_path_object, handle, indent=4)
		except Exception as exception:
			messagebox.showerror("Show Paths Error:", exception)
			return

	# Deletes the path of the file extension currently in the text box, if any.
	def delete_path(self):
		try:
			file_extension = self.file_extension.get()
			if str(file_extension) == "":
				messagebox.showinfo("Information", "Please enter a file extension to delete.")
				return
			else:
				iterator = 0
				deleted_record = False
				with open('{}Paths.JSON'.format(FileMover.FILE_BASE)) as handle:
					json_path_object = json.load(handle)
				for path_object in json_path_object['path_object']:
					if path_object['file_extension'] == file_extension:
						json_path_object['path_object'].pop(iterator)
						deleted_record = True
					iterator += 1
				with open('{}Paths.JSON'.format(FileMover.FILE_BASE), 'w') as handle:
					json.dump(json_path_object, handle, indent=4)
					if deleted_record is True:
						messagebox.showinfo("Information", "Deleted {} from the list of file extensions.".format(file_extension))
					else:
						messagebox.showinfo("Information", "{} was not found in the list of file extensions.".format(file_extension))
				return
		except Exception as exception:
			messagebox.showerror("Delete Path Error:", exception)
			return

	# Sets the path of the file extension currently in the text box, if any.
	def set_path(self):
		try:
			file_extension = self.file_extension.get()
			if str(file_extension) == "":
				messagebox.showinfo("Information", "Please enter a file extension.")
				return
			else:
				with open('{}Paths.JSON'.format(FileMover.FILE_BASE)) as handle:
					json_path_object = json.load(handle)
					json_path_object['path_object'].append({
						'file_extension' : file_extension,
						'location_path' : FileMover.location_path,
						'destination_path' : FileMover.destination_path
					})
				with open('{}Paths.JSON'.format(FileMover.FILE_BASE), 'w') as handle:
					json.dump(json_path_object, handle, indent=4)
				return
		except ValueError: # Fills the JSON object with a default path when no other paths exist.
			json_path_object = {}
			json_path_object['path_object'] = []
			json_path_object['path_object'].append({
			'file_extension' : 'extension',
			'location_path' : 'current location',
			'destination_path' : 'destination location'
			})
			with open('{}Paths.JSON'.format(FileMover.FILE_BASE), 'w') as handle:
				json.dump(json_path_object, handle, indent=4)
		except NameError as exception:
			messagebox.showinfo("Information", "Please browse for a file destination for {}".format(re.findall(r"'(.*?)'", str(exception), re.DOTALL)))
		except Exception as exception:
			messagebox.showerror("Set Path Error:", exception)
			return

	# Move all files types to their desired locations, determined by Paths.JSON.
	def move_files(self):
		try:
			while True:
				pathlist = []
				with open('{}Paths.JSON'.format(FileMover.FILE_BASE)) as handle:
					json_path_object = json.load(handle)
				for element in json_path_object['path_object']:
					rootPath = element['location_path']
					files = [i for i in os.listdir(rootPath) if os.path.isfile(os.path.join(rootPath, i))]
					for file in files:
						if search("desktop.ini", file.lower()):
							continue
						elif search(element['file_extension'], str(magic.from_file(os.path.join(rootPath, file), mime=True)).lower()):
							path = os.path.join(element['destination_path'], element['file_extension'])
							print(path)
							if not os.path.exists(path):
								os.mkdir(path)
							shutil.move(os.path.join(rootPath, file), (element['destination_path'] + '\\' + element['file_extension']))
		except Exception as exception:
			messagebox.showerror("Move Files Error:", exception)
			return

# Calls the class to run the program.
FileMover()
