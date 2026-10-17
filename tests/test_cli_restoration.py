import configparser,importlib.util,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from utils.web_settings import defaults
from utils import automatic_metadata as auto
ROOT=Path(__file__).resolve().parents[1]

class RestoredCliTests(unittest.TestCase):
 def setUp(self):
  (ROOT/'tmp').mkdir(exist_ok=True);self.temp=tempfile.TemporaryDirectory(dir=ROOT/'tmp');self.root=Path(self.temp.name)
  self.library=self.root/'library';self.library.mkdir();self.release=self.library/'Example.Movie.2024.1080p.WEB-DL.x264-GROUP';self.release.mkdir();(self.release/'video.mkv').write_bytes(b'payload')
  self.config=defaults();self.config.set('Paths','DATADIR',str(self.library));self.config.set('Paths','TMP_DIR',str(self.root/'scratch'));self.config.set('Paths','UPLOADLOG',str(self.root/'logs'/'upload.log'));self.config.set('TMDB','TOKEN','example-token')
  self.local=patch.object(auto,'extract_metadata',return_value={'release_year':'2024'});self.local.start()
 def tearDown(self):self.local.stop();self.temp.cleanup()
 def test_movie_cli_searches_and_uses_detail(self):
  with patch.object(auto.tmdb,'search',return_value=[{'id':'1','title':'Example Movie','date':'2024'}]) as search,patch.object(auto.tmdb,'detail',return_value={'metadata':{'imdbId':'tt1234567'},'description':'Plot','images':['https://image.tmdb.org/cover.jpg']}):
   job,images=auto.enrich(self.release,6,{},self.config)
  search.assert_called_once_with('example-token','Example Movie','movie');self.assertEqual(job['metadata']['imdbId'],'tt1234567');self.assertEqual(job['description'],'Plot');self.assertEqual(len(images),1)
 def test_explicit_web_selection_and_nfo_take_precedence(self):
  for metadata in [{'imdbId':'tt7654321'},{'gameUrl':'https://www.igdb.com/games/example'}]:
   with patch.object(auto.tmdb,'search') as movie,patch.object(auto.igdb,'search') as game:
    result,images=auto.enrich(self.release,25 if 'gameUrl' in metadata else 6,{'metadata':metadata,'description':'My text','images':['https://example.invalid/cover.png']},self.config)
   movie.assert_not_called();game.assert_not_called();self.assertEqual(result['description'],'My text');self.assertEqual(images,[])
  self.local.stop()
  (self.release/'info.nfo').write_text('https://www.imdb.com/title/tt1234567/')
  with patch.object(auto.tmdb,'search') as search,patch('utils.release_metadata.runtime_minutes',return_value='90'):
   job,_=auto.enrich(self.release,6,{},self.config)
  search.assert_not_called();self.assertEqual(job['metadata']['imdbId'],'tt1234567')
 def test_game_cli_fetches_text_cover_and_screenshots(self):
  game=self.library/'Example.Game.NSW.NSP-GROUP';game.mkdir();self.config.set('IGDB','CLIENT_ID','id');self.config.set('IGDB','CLIENT_SECRET','secret')
  with patch.object(auto.igdb,'search',return_value=[{'id':'1','title':'Example Game'}]) as search,patch.object(auto.igdb,'detail',return_value={'metadata':{'gameUrl':'https://www.igdb.com/games/example'},'description':'Game plot','images':['https://images.igdb.com/cover.jpg','https://images.igdb.com/frame.jpg']}):
   job,images=auto.enrich(game,25,{},self.config)
  search.assert_called_once_with('id','secret','Example Game');self.assertEqual(len(images),2);self.assertEqual(job['description'],'Game plot')
 def test_tvmaze_fallback_and_lookup_failure_do_not_break_uploads(self):
  with patch.object(auto.tmdb,'search',return_value=[]),patch.object(auto.tvmaze,'search',return_value=[{'id':'2','title':'Example Movie'}]),patch.object(auto.tvmaze,'detail',return_value={'metadata':{'imdbId':'tt7654321'}}):
   job,_=auto.enrich(self.release,8,{},self.config)
  self.assertEqual(job['metadata']['imdbId'],'tt7654321')
  with patch.object(auto.tmdb,'search',side_effect=ValueError('unavailable')):
   job,images=auto.enrich(self.release,6,{'description':'Preserve'},self.config)
  self.assertEqual(job['description'],'Preserve');self.assertEqual(images,[])
 def test_tmdb_legacy_api_key_authentication(self):
  from utils import tmdb
  session=Mock();session.__enter__=Mock(return_value=session);session.__exit__=Mock(return_value=False);session.get.return_value.status_code=200;session.get.return_value.json.return_value={}
  with patch.object(tmdb.requests,'Session',return_value=session):tmdb.request('a'*32,'/search/movie',{'query':'Example'})
  self.assertEqual(session.get.call_args.kwargs['params']['api_key'],'a'*32);self.assertNotIn('Authorization',session.get.call_args.kwargs['headers'])
 def test_auto_category_uses_mp3_content(self):
  from utils.category_utils import determine_category
  folder=self.library/'Unknown.Release';folder.mkdir();(folder/'track.mp3').write_bytes(b'music')
  self.assertEqual(determine_category(folder.name,directory=folder)[1],'22')
  import uploader
  self.assertEqual(uploader.validate_job(folder,None,config=self.config)['category'],22)
 def test_explicit_directory_staging_modes_and_collision(self):
  from utils.cli_sources import stage
  for mode in ['link','copy','move']:
   source=self.root/('Source-'+mode);source.mkdir();(source/'file.txt').write_text('content')
   result=Path(stage(source,self.config,mode));self.assertEqual((result/'file.txt').read_text(),'content')
   if mode=='link':self.assertTrue((source/'file.txt').samefile(result/'file.txt'))
   if mode=='move':self.assertFalse(source.exists())
   else:self.assertTrue(source.exists())
   if mode!='move':
    with self.assertRaises(ValueError):stage(source,self.config,mode)
 def test_screenshots_try_next_video_after_failure(self):
  from utils import screenshot_utils as shots
  first=self.release/'large.mkv';first.write_bytes(b'x'*100);second=self.release/'small.mkv';second.write_bytes(b'x'*10)
  with patch.object(shots,'ConfigLoader') as loader,patch.object(shots,'generate_candidate',side_effect=[RuntimeError('corrupt'),None]) as generate:
   loader.return_value.get_config.return_value=self.config;shots.generate_screenshots(self.release,6)
  self.assertEqual(generate.call_count,2);self.assertNotEqual(generate.call_args_list[0].args[0],generate.call_args_list[1].args[0])
 def test_original_rar_mode_preserves_payload(self):
  from utils import unpacked_source
  (self.release/'release.rar').write_bytes(b'archive')
  self.config.set('UnrarUpload','ENABLED','false');self.config.set('UnrarUpload','MODE','original_only')
  with patch.object(unpacked_source,'ConfigLoader') as loader:
   loader.return_value.get_config.return_value=self.config
   self.assertEqual(unpacked_source.prepare_source(self.release,self.root/'log'),(self.release,None))
   unpacked_source.assert_unpacked_torrent(Mock(files=[Path('release.rar')]))
 def test_tls_certificate_is_preserved_and_service_uses_it(self):
  spec=importlib.util.spec_from_file_location('tls_script',ROOT/'scripts/tls.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  folder=self.root/'certificates';folder.mkdir();(folder/'cert.pem').write_text('cert');(folder/'key.pem').write_text('key')
  with patch.object(module.subprocess,'run') as run:module.create('seedbox.example.com',self.root)
  run.assert_not_called();self.assertEqual((folder/'key.pem').read_text(),'key')
  from scripts.service import unit
  self.assertIn('--tls-cert',unit(ROOT,ROOT/'python','127.0.0.1',6080,folder/'cert.pem',folder/'key.pem'))
 def test_real_fastresume_preserves_info_hash(self):
  if os.name=='nt':self.skipTest('Bundled mkbrr is Linux only')
  from utils import torrent_utils
  from utils.fastresume_utils import add_fastresume
  from utils.torrent_metadata import TorrentMetadata
  self.config.set('Torrent','ANNOUNCEURL','https://example.invalid/announce/test')
  with patch.object(torrent_utils,'config',self.config):torrent,_=torrent_utils.create_torrent(self.release,self.root/'hashed',False,'mkbrr')
  before=TorrentMetadata.read(torrent).infohash;output=self.root/'resume.torrent'
  from utils import fastresume_utils
  with patch.object(fastresume_utils,'config',self.config):self.assertTrue(add_fastresume(torrent,str(self.library),str(output)))
  self.assertEqual(TorrentMetadata.read(output).infohash,before)

 def test_cli_accepts_auto_category_without_cat(self):
  import uploader,sys
  folder=self.library/'Album';folder.mkdir();(folder/'track.mp3').write_bytes(b'music')
  with patch.object(sys,'argv',['uploader.py','upload',str(folder),'--dry-run']),patch.object(uploader,'load_config',return_value=self.config),patch.object(uploader,'ensure_config'),patch.object(uploader,'check_config',return_value=[]):
   self.assertEqual(uploader.main(),0)
 def test_rar_preview_unmounts_without_touching_original(self):
  from utils import rar_preview
  (self.release/'release.rar').write_bytes(b'original archive')
  with patch.object(rar_preview,'iter_media_files',return_value=[]),patch.object(rar_preview,'run_mount_command') as mount,patch.object(rar_preview,'preview_error',return_value=''),patch.object(rar_preview.os.path,'ismount',return_value=True),patch.object(rar_preview,'unmount_path',return_value=True) as unmount:
   with rar_preview.media_directory(self.release,30,self.config) as view:self.assertNotEqual(view,self.release)
  mount.assert_called_once();unmount.assert_called_once();self.assertEqual((self.release/'release.rar').read_bytes(),b'original archive')
 def test_real_self_signed_certificate_can_be_loaded(self):
  import shutil,ssl
  if not shutil.which('openssl'):self.skipTest('OpenSSL required')
  spec=importlib.util.spec_from_file_location('tls_real',ROOT/'scripts/tls.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  cert,key=module.create('localhost',self.root);context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(cert,key)
  self.assertTrue(cert.is_file());self.assertTrue(key.is_file())
 def test_update_notification_uses_new_repository(self):
  from utils import update_check
  with patch.object(update_check.requests,'get') as request,patch('builtins.print') as emit:
   request.return_value.status_code=200;request.return_value.json.return_value={'tag_name':'v99.0.0'};update_check.check('3.0.0')
  self.assertIn('/DigiCore404/digitalcore-uploader/',request.call_args.args[0]);emit.assert_called_once()

 def test_configured_mtn_failure_retries_bundled_tool(self):
  from utils import screenshot_utils, mtn_screenshots
  self.config.set('MediaTools','MTNBIN','/example/mtn');self.config.set('MediaTools','SCREENSHOT_ENGINE','mtn')
  target=self.root/'shots';target.mkdir()
  with patch.object(screenshot_utils.subprocess,'run',return_value=Mock(stdout='{"format":{"duration":"60"}}')),patch.object(mtn_screenshots,'generate',side_effect=[RuntimeError('bad tool'),None]) as generate:
   screenshot_utils.generate_candidate(self.release/'video.mkv',target,self.config)
  self.assertEqual(generate.call_count,2);self.assertEqual(generate.call_args.args[3].get('MediaTools','MTNBIN'),'');self.assertEqual(self.config.get('MediaTools','MTNBIN'),'/example/mtn')
