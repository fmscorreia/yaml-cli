import sys
from ruamel.yaml import YAML


## ============================================================
## ----- Error messages ---------------------------------------

INVALID_NUMBER_ARGS = "Invalid number of arguments for command %s: %d"
NO_FLAGS_OR_ARGS_SPECIFIED = "No flags or arguments specified for command: %s"
INVALID_FLAG = "Invalid flag \'%s\' for command: %s"
FILE_NOT_FOUND = "File not found: %s"
NO_COMMAND_PROVIDED = "No command provided"
INVALID_COMMAND = "Invalid command: %s"
INVALID_MERGE_OP = "Invalid merge operation: %s"
INVALID_KEY = "Invalid key: %s"


## ============================================================
## ----- Utility functions ------------------------------------

def usage():
  help = f"""\
\nUsage: {sys.argv[0]} [flags] command

Commands:

  read file node
    Print a node

  write [-i] file node-path new-node
    Add a new node, or overwrite existing node

    Flags:
      -i,   edit file in place

  append [-i] file node-path new-node
    Add a value to an existing node

    Flags:
      -i,   edit file in place

  merge [-i] append|overwrite file node-path other-file
    Merge file with other-file

    Flags:
      -i,   edit file in place

  delete [-i] file node-path
    Delete a node

    Flags:
      -i,   edit file in place

  help
    Get help
"""
  print (help)


def exit_invalid_arg_number(command, argc):
  print(f"{INVALID_NUMBER_ARGS}" %(command, argc))
  sys.exit(2)


def exit_no_flags_or_args_specified(command):
  print(f"{NO_FLAGS_OR_ARGS_SPECIFIED}" %(command))
  sys.exit(2)


def exit_invalid_flag(command, flag):
  print(f"{INVALID_FLAG}" %(flag, command))
  sys.exit(2)


def exit_file_not_found(filename):
  print(f"{FILE_NOT_FOUND}" %(filename))
  sys.exit(1)


def exit_no_command_provided():
  print(f"{NO_COMMAND_PROVIDED}")
  sys.exit(2)


def exit_invalid_command(command):
  print(f"{INVALID_COMMAND}" %(command))
  sys.exit(2)


def exit_invalid_merge_op(op):
  print(f"{INVALID_MERGE_OP}" %(op))
  sys.exit(2)


def exit_invalid_key(key):
  print(f"{INVALID_KEY}" %(key))
  sys.exit(1)


def argv_to_flags_args_tuple():
  if len(sys.argv) < 3:
    exit_no_flags_or_args_specified(command)
  if sys.argv[2][0] == '-':
    return (list(sys.argv[2][1:]), sys.argv[3:])
  else:
    return ([], sys.argv[2:])


def get_node_reference(root, path):
  if len(path) < 1:
    return root
  else:
    head, *tail = path
    try:
      return get_node_reference(root[head], tail)
    except KeyError:
      exit_invalid_key(head)


def dump_aux_inplace(content, filename):
  with open(filename, 'w') as f:
    if isinstance(content, str):
      # yaml.dump prints '...' end markers for some single scalars
      f.write(content)
    else:
      yaml.dump(content, f)

def dump_aux(content):
  if isinstance(content, str):
    # yaml.dump prints '...' end markers for some single scalars
    print(content)
  else:
    yaml.dump(content, sys.stdout)



## ============================================================
## ----- Command functions ------------------------------------


def read():
  (flags, args) = argv_to_flags_args_tuple()

  if len(args) != 2:
    exit_invalid_arg_number(command, len(args))

  if len(flags) > 0:
    exit_invalid_flag(command, flags[0])

  filename = args[0]
  node_path = args[1].split(".")

  try:
    with open(filename) as f:
      config = yaml.load(f)
  except FileNotFoundError:
    exit_file_not_found(filename)

  node_ref = get_node_reference(config, node_path)
  dump_aux(node_ref)


def write():
  (flags, args) = argv_to_flags_args_tuple()
  inplace = False

  if len(args) != 3:
    exit_invalid_arg_number(command, len(args))

  for flag in flags:
    if flag == 'i':
      inplace = True
    else:
      exit_invalid_flag(command, flag)

  filename = args[0]
  node_path = args[1].split(".")
  new_node = yaml.load(f"""{args[2]}""")

  try:
    with open(filename) as f:
      config = yaml.load(f)
  except FileNotFoundError:
    exit_file_not_found(filename)

  node_ref = get_node_reference(config, node_path[0:-1])
  try:
    node_ref[node_path[-1]] = new_node
  except KeyError:
    exit_invalid_key(node_path[-1])

  if inplace:
    dump_aux_inplace(config, filename)
  else:
    dump_aux(config)


def append():
  (flags, args) = argv_to_flags_args_tuple()
  inplace = False

  if len(args) != 3:
    exit_invalid_arg_number(command, len(args))

  for flag in flags:
    if flag == 'i':
      inplace = True
    else:
      exit_invalid_flag(command, flag)

  filename = args[0]
  node_path = args[1].split(".")
  seq = yaml.load(f"""{args[2]}""")

  try:
    with open(filename) as f:
      config = yaml.load(f)
  except FileNotFoundError:
    exit_file_not_found(filename)

  node_ref = get_node_reference(config, node_path)
  node_ref += seq

  if inplace:
    dump_aux_inplace(config, filename)
  else:
    dump_aux(config)


def merge():
  (flags, args) = argv_to_flags_args_tuple()
  inplace = False

  if len(args) != 4:
    exit_invalid_arg_number(command, len(args))

  for flag in flags:
    if flag == 'i':
      inplace = True
    else:
      exit_invalid_flag(command, flag)

  op = args[0]
  if op != "append" and op != "overwrite":
    exit_invalid_merge_op(op)

  filename = args[1]
  node_path = args[2].split(".")
  other_filename = args[3]

  try:
    with open(filename) as f:
      config = yaml.load(f)
  except FileNotFoundError:
    exit_file_not_found(filename)
  try:
    with open(other_filename) as f:
      other = yaml.load(f)
  except FileNotFoundError:
    exit_file_not_found(filename)

  if op == "append":
    node_ref = get_node_reference(config, node_path)
    node_ref += other
  elif op == "overwrite":
    node_ref = get_node_reference(config, node_path[0:-1])
    try:
      node_ref[node_path[-1]] = other
    except KeyError:
      exit_invalid_key(node_path[-1])


  if inplace:
    dump_aux_inplace(config, filename)
  else:
    dump_aux(config)


def delete():
  (flags, args) = argv_to_flags_args_tuple()
  inplace = False

  if len(args) != 2:
    exit_invalid_arg_number(command, len(args))

  for flag in flags:
    if flag == 'i':
      inplace = True
    else:
      exit_invalid_flag(command, flag)

  filename = args[0]
  node_path = args[1].split(".")

  try:
    with open(filename) as f:
      config = yaml.load(f)
  except FileNotFoundError:
    exit_file_not_found(filename)

  node_ref = get_node_reference(config, node_path[0:-1])
  try:
    del node_ref[node_path[-1]]
  except KeyError:
    exit_invalid_key(node_path[-1])

  if inplace:
    dump_aux_inplace(config, filename)
  else:
    dump_aux(config)


## ============================================================
## ----- Input validation and flow selection ------------------

if len(sys.argv) < 2:
  exit_no_command_provided()

yaml = YAML()
yaml.preserve_quotes = True

command = sys.argv[1]

if command == "read":
  read()
elif command == "write":
  write()
elif command == "append":
  append()
elif command == "merge":
  merge()
elif command == "delete":
  delete()
elif command == "help":
  usage()
else:
  exit_invalid_command(command)
