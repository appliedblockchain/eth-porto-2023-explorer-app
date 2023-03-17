def fmt_hash(hash):
  hash_str = hash.hex()
  hash_str = f'{hash_str[0:7]}...{hash_str[-2:]}'
  return hash_str

def fmt_hash_str(hash_str):
  hash_str = f'{hash_str[0:7]}...{hash_str[-2:]}'
  return hash_str
