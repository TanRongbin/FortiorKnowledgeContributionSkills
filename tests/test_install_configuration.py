import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('contributor_installer',ROOT/'install.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
class ConfigTests(unittest.TestCase):
    def test_update_preserves_submission_mode_endpoint_and_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);(home/'.fortior').mkdir();p=home/'.fortior/knowledge-contributor.env';p.write_text('FORTIOR_SUBMIT_MODE=local_only\nFORTIOR_CONTRIBUTION_ENDPOINT=http://localhost:1234\nTOKEN=private\nFORTIOR_CLIENT_INSTANCE_ID=existing\n',encoding='utf-8')
            with patch.object(installer,'HOME',home):installer.ensure_local_config()
            text=p.read_text();self.assertIn('FORTIOR_SUBMIT_MODE=local_only',text);self.assertIn('http://localhost:1234',text);self.assertIn('TOKEN=private',text);self.assertIn('INSTANCE_ID=existing',text)
    def test_new_config_created_without_submitting_anything(self):
        with tempfile.TemporaryDirectory() as d,patch.object(installer,'HOME',Path(d)):
            p=installer.ensure_local_config();self.assertTrue(p.is_file());self.assertTrue(installer.config_value(p,'FORTIOR_CLIENT_INSTANCE_ID'))
    def test_multiple_destinations_restore_if_runtime_activation_fails(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);source=home/'source';source.mkdir();(source/'SKILL.md').write_text('test')
            (source/'config.example.env').write_text('FORTIOR_CLIENT_INSTANCE_ID=\n')
            a=home/'a/skill';b=home/'b/skill';a.mkdir(parents=True);(a/'SKILL.md').write_text('old');b.mkdir(parents=True);(b/'unrelated').write_text('keep')
            with patch.object(installer,'HOME',home),patch.object(installer,'SOURCE',source),patch.object(installer,'source_identity',return_value={'commit':'a'*40,'dirty':False}):
                with self.assertRaises(ValueError):installer.install_destinations([a,b],replace=True)
            self.assertEqual((a/'SKILL.md').read_text(),'old');self.assertTrue((b/'unrelated').exists())
