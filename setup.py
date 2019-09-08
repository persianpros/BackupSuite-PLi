from distutils.core import setup
import setup_translate

pkg = 'Extensions.BackupSuite'
setup (name = 'enigma2-plugin-extensions-backupsuite',
       version = '1.0',
       description = 'Back-up tool for various enigma2 receivers',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg: ['*.sh', '*.txt', 'mphelp.xml', 'plugin.png', '*/*.png', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )
