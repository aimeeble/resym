import os
import sys


def verify_link(symlink_filename):
   real_filename = os.path.realpath(symlink_filename)

   if os.path.exists(real_filename):
      return True

   print 'symlink: %s' % (symlink_filename)
   print '\tInvalid target %s' % (real_filename)
   return False


def find_links(roots, ignores=[]):
   for root in roots:
      for entry in os.walk(root):
         for filename in entry[2]:
            abs_filename = os.path.abspath(os.path.join(entry[0], filename))
            if not os.path.islink(abs_filename):
               continue
            verify_link(abs_filename)


if __name__ == '__main__':
   if len(sys.argv) < 2:
      sys.exit(1)

   roots = [sys.argv[1]]
   find_links(roots)
