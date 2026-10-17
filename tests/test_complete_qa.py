import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from utils.web_settings import defaults
from utils import automatic_metadata,cli_sources,rar_preview
ROOT=Path(__file__).resolve().parents[1]
class CompleteQaTests(unittest.TestCase):
 def setUp(self):
  (ROOT/'tmp').mkdir(exist_ok=True);self.temp=tempfile.TemporaryDirectory(dir=ROOT/'tmp');self.root=Path(self.temp.name);self.folder=self.root/'Example.S01E01';self.folder.mkdir();self.config=defaults();self.config.set('Paths','DATADIR',str(self.root))
 def tearDown(self):self.temp.cleanup()
 def test_legacy_link_option_accepts_release_name_inside_datadir(self):
  self.assertEqual(Path(cli_sources.stage(self.folder.name,self.config,'link')),self.folder.resolve())
  self.assertFalse(self.folder.is_symlink())
 def test_tvmaze_is_tried_when_tmdb_is_unavailable(self):
  self.config.set('TMDB','TOKEN','example-token')
  with patch.object(automatic_metadata,'extract_metadata',return_value={}),patch.object(automatic_metadata.tmdb,'search',side_effect=ValueError('unavailable')),patch.object(automatic_metadata.tvmaze,'search',return_value=[{'id':'1','title':'Example'}]) as search,patch.object(automatic_metadata.tvmaze,'detail',return_value={'metadata':{'imdbId':'tt1234567'}}):
   job,_=automatic_metadata.enrich(self.folder,8,{},self.config)
  search.assert_called_once_with('Example');self.assertEqual(job['metadata']['imdbId'],'tt1234567')
 def test_rar_without_fuse_has_clear_preflight_and_local_video_bypasses_it(self):
  (self.folder/'release.rar').write_bytes(b'archive')
  with patch.object(rar_preview.Path,'exists',return_value=False):
   self.assertIn('/dev/fuse',rar_preview.preview_error(self.folder,30,self.config))
  (self.folder/'preview.mp4').write_bytes(b'video')
  with patch.object(rar_preview.Path,'exists',return_value=False):
   self.assertEqual(rar_preview.preview_error(self.folder,30,self.config),'')

 def test_docker_helper_uses_mounted_config_and_maps_callback_and_watch_paths(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('qa_docker',ROOT/'docker-run.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  for args in [['upload',str(self.folder)],['completed',str(self.folder),'--hash','a'*40],['watch','--cat','6','--folder',str(self.folder)]]:
   command=module.command(args,self.config)
   self.assertIn('DIGITALCORE_CONFIG=/app/config.ini',command);self.assertIn('DIGITALCORE_CONTAINER=1',command);self.assertIn('/content/'+self.folder.name,command)

 def test_native_checkout_does_not_claim_an_incomplete_mtn_wrapper(self):
  from utils import runtime_tools
  folder=self.root/'bin/mtn';folder.mkdir(parents=True);(folder/'mtn').write_text('#!/bin/sh\nexec "$directory/mtn.bin" "$@"\n')
  with patch.object(runtime_tools,'ROOT',self.root),patch.object(runtime_tools.platform,'system',return_value='Linux'),patch.object(runtime_tools.platform,'machine',return_value='x86_64'),patch.object(runtime_tools.os,'access',return_value=True),patch.object(runtime_tools.shutil,'which',return_value=None):
   self.assertIsNone(runtime_tools.find_tool('mtn',self.config));(folder/'mtn.bin').write_bytes(b'ELF fixture');self.assertEqual(runtime_tools.find_tool('mtn',self.config),str(folder/'mtn'))
 def test_native_setup_chooses_ffmpeg_only_for_fresh_configuration(self):
  import configparser
  from utils import native_setup
  path=self.root/'config.ini';original='[Website]\nAPI_KEY = test-preserve\n';path.write_text(original)
  with patch.object(native_setup,'find_tool',return_value=None):
   with self.assertRaises(ValueError):native_setup.configure(path,new=False)
   self.assertEqual(path.read_text(),original);self.assertEqual(native_setup.configure(path,new=True),'ffmpeg')
  result=configparser.ConfigParser();result.read(path);self.assertEqual(result.get('Website','API_KEY'),'test-preserve');self.assertEqual(result.get('MediaTools','SCREENSHOT_ENGINE'),'ffmpeg')
