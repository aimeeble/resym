import os
import sys


class FixSymLinks(object):
   '''Finds symlinks under roots and makes sure they are relative links if
   possible.

   For every symlink under every root (which isn't also under an ignored root),
   check to see if the file it points at is also under the same root.  If so,
   then it is considered safe to re-link it using a relative path.

   For example,
      1. /home/username/foo.txt -> /home/username/files/foo.txt changes to,
         /home/username/foo.txt -> files/foo.txt
      2. /home/username/files/bar.txt -> /home/username/bar.txt changes to,
         /home/username/files/bar.txt -> ../bar.txt
   '''

   def __init__(self, roots, ignores=[], yes_to_all=False, dryrun=False, verbose=False):
      self.roots = roots
      self.ignores = ignores
      self.yes_to_all = yes_to_all
      self.verbose = verbose
      self.dryrun = dryrun

   def _is_ignored(self, path):
      '''Checks to see if the specified path is under an ignore root.

      '''
      for ignore_root in self.ignores:
         prefix = os.path.commonprefix([ignore_root, path])
         if prefix == ignore_root:
            if self.verbose:
               print 'ignoring %s' % (path)
            return True
         return False

   def _generate_list(self):
      '''Generates a list of files we intend to consider.

      This will be a list of files that meet the properties described at the
      class-level comment.  The result will be a list of the form:
         [(symlink filename, actual filename), ...]

      '''
      file_list = []
      for root in self.roots:
         for entry in os.walk(root):
            for filename in entry[2]:
               symlink_filename = os.path.abspath(os.path.join(entry[0], filename))

               # Only fix symlinks.
               if not os.path.islink(symlink_filename):
                  continue

               # ... and we aren't ignoring this path.
               if self._is_ignored(symlink_filename):
                  continue

               # ... and only touch absolute links
               # ... and only if it points at a real file.
               real_filename = os.path.realpath(symlink_filename)
               if not os.path.isabs(real_filename):
                  continue
               if not os.path.exists(real_filename):
                  continue

               # ... and only if the real file is under our root.
               prefix = os.path.commonprefix([root, real_filename])
               if prefix != root:
                  continue

               file_list.append((symlink_filename, real_filename))
      return file_list

   def _prompt(self, symlink_filename, real_filename):
      '''Prompts for what action to take in a specific instance.

      '''
      if self.yes_to_all:
         return 'y'

      while True:
         inp = raw_input('Fix %s -> %s [Y,a,n,q]? ' % (symlink_filename, real_filename))
         if not inp:
            return 'y'
         inp = inp.lower()[0]
         if inp not in ['y','a','n','q']:
            continue
         return inp

   def _points_at_same_file(self, symlink_filename, rel_real_filename):
      '''Checks that the file pointed to by the symlink is the same as what the
      new filename is pointing at when computed relative to the folder holding
      the symlink itself.

      '''
      dest_dirname = os.path.dirname(symlink_filename)

      abs_real_filename = os.path.join(dest_dirname, rel_real_filename)
      abs_real_filename = os.path.realpath(abs_real_filename)
      abs_real_filename = os.path.normpath(abs_real_filename)

      original_filename = os.path.realpath(symlink_filename)
      original_filename = os.path.abspath(original_filename)
      original_filename = os.path.normpath(original_filename)

      if abs_real_filename != original_filename:
         if self.verbose:
            print '%s != %s' % (abs_real_filename, original_filename)
         return False
      return True

   def _fix_link(self, symlink_filename, real_filename):
      '''Fixes a specific symlink.

      This will first unlink the existing symlink, then re-symlink using a
      relative path to the same file.  A sanity check is performed.

      '''

      if os.path.isabs(real_filename):
         raise Exception("real filename is not relative")
      if not self._points_at_same_file(symlink_filename, real_filename):
         raise Exception("cannot change file being pointed at")

      try:
         if self.verbose:
            print 'ln -sf %s %s' % (real_filename, symlink_filename)
         if not self.dryrun:
            os.unlink(symlink_filename)
            os.symlink(real_filename, symlink_filename)
      except:
         print 'Error symlinking %s -> %s' % (real_filename, symlink_filename)

   def fix_all_links(self):
      '''Generates a list of files, prompts the user for action, then does
      stuff.

      '''
      files_to_fix = self._generate_list()

      for symlink_filename,real_filename in files_to_fix:
         rel_real_filename = os.path.relpath(real_filename,
               start=os.path.dirname(symlink_filename))

         choice = self._prompt(symlink_filename, rel_real_filename)

         if choice == 'a':
            # if 'a' (yes to all), stop asking and say 'y' for this instance.
            self.yes_to_all = True
            choice = 'y'

         if choice == 'y':
            self._fix_link(symlink_filename, rel_real_filename)
         elif choice == 'n':
            continue
         elif choice == 'q':
            return


if __name__ == '__main__':
   if len(sys.argv) < 2:
      sys.exit(1)

   # Walk the command-line arguments.  Each argument is treated as a path. Ones
   # that begin with - (minus) are considered ignore paths; those which do not
   # are considered valid roots.
   roots = []
   ignores = []
   for path in sys.argv[1:]:
      if path[0] == '-':
         path = path[1:]
         path = os.path.expanduser(path)
         path = os.path.expandvars(path)
         ignores.append(os.path.abspath(path))
      else:
         path = os.path.expanduser(path)
         path = os.path.expandvars(path)
         roots.append(os.path.abspath(path))

   print 'root = %s' % str(roots)
   print 'ignore = %s' % str(ignores)

   fsl = FixSymLinks(roots, ignores=ignores)
   fsl.fix_all_links()
