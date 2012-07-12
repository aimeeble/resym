resym
=====

Re-create symlinks to be relative.

Finds symlinks under roots and makes sure they are relative links if
possible.

For every symlink under every root (which isn't also under an ignored root),
check to see if the file it points at is also under the same root.  If so,
then it is considered safe to re-link it using a relative path.

For example,

   1. /home/username/foo.txt -> /home/username/files/foo.txt changes to,
      /home/username/foo.txt -> files/foo.txt

   2. /home/username/files/bar.txt -> /home/username/bar.txt changes to,
      /home/username/files/bar.txt -> ../bar.txt
