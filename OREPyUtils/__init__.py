import sys

from Helper import Info, Severe

import PersistentData

from ast import literal_eval as Eval
import traceback

Failiures = {}

DATA_PATH = "plugins/OREUtilsV2.py.dir/Data/"

class ConfigFile(PersistentData.NodeFile):
	def __init__(self):
		PersistentData.NodeFile.__init__(self, DATA_PATH + "config.json")

		if 'properties' not in self.node:
			self.node.New('properties')
	
	def __getitem__(self, name):
		return self.node.properties.Get(name)

	def __setitem__(self, name, value):
		self.node.properties.Set(name, value)

CONFIG	= ConfigFile()

CONFIG.node.properties.Ensure("Include", {})
Include = [key for key,value in CONFIG["Include"].iteritems() if value]


def ImportFiles():
	for N in Include:
		try:
			exec 'import ' + N

		except Exception, E:
			Severe('[!]Error importing ' + N)

			Failiures[N] = str(E)
	
		else:
			Info('[i]Imported ' + N)

def Load(plugin, **kwargs):
	if plugin not in Failiures and plugin in Include:
		print(plugin)
		#try:
		exec plugin + '.OnEnable(**kwargs)'
		
		#except Exception, E:
		#	Severe('[!]Error with ' + plugin + ' '+str(E))

		#	Failiures[plugin] = str(E)

def Unload(plugin, **kwargs):
	if plugin not in Failiures and plugin in Include:
		try:
			exec plugin + '.OnDisable(**kwargs)'

		except Exception, E:
			Severe('[!]Error with ' + plugin + ' ' + str(E))
#temp
def TryExec(*args):pass
		
def CheckIsString(property, plugin):
	if isinstance(CONFIG[property], str):
		return True

	else:
		Severe('[!]No ' + property + ' in config')

		Failiures[plugin] = 'No ' + property + ' in config'

		return False


ImportFiles()

@hook.command('property', description='Plugin properties')
def onCommandProperty(sender, args):
	if not sender.hasPermission("ore.config"):
		sender.sendMessage("No permission!")
		return True

	if len(args) == 0:
		sender.sendMessage(str(CONFIG).replace('\t',' '))

	elif len(args) == 1:
		sender.sendMessage(args[0] + " = " + str(CONFIG[args[0]]))
	
	elif len(args) >= 2:
		if args[1] == 'None':
			CONFIG[args[0]] = None

		else:
			try:
				value = Eval(' '.join(args[1:]))
			except:
				traceback.print_exc()
				sender.sendMessage('Usage: /property [name] [value]')
			else:
				CONFIG[args[0]] = value

	return True

@hook.command('status', description = 'View module loading failiures')
def OnCommandFail(sender, args):
	if len(args) == 1:
		if args[0] in Failiures:
			sender.sendMessage('[!!]Module failed: ' + Failiures[Args[0]])
		
		elif args[0] in Include:
			
			sender.sendMessage('All is good')
		
		else:
			sender.sendMessage('[!]Unknown module')

	else:	
		if not Failiures:
			sender.sendMessage("All is good")

		else:
			for Fail, Reason in Failiures.iteritems():
				sender.sendMessage('[!!]' + Fail + ' has failed: ' + Reason)

	return True
	
@hook.enable
def OnEnable():
	Load('Plots')
	Load('IRCBot', conf=CONFIG)	
	Load('Inventory')
	Load('EventHooks', conf=CONFIG)
	Load('Derps', conf=CONFIG)

	CheckIsString('DerpPath', 'Derps')
	TryExec('Derps',
		'LoadDerps(ConvertPath(CONFIG["DerpPath"]))')

	CheckIsString('HelpPath', 'UsefulCommands')
	TryExec('UsefulCommands', 
		'LoadHelp(ConvertPath(CONFIG["HelpPath"]))')

@hook.disable
def OnDisable():
	CONFIG.Dump()

	Unload('Plots')
	Unload('IRCBot')
	Unload('Inventory')
