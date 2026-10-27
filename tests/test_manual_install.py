"""Local filesystem/update contracts; no host/model or production freshness proof."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/fortior-knowledge-contributor/scripts'))
import local_identity as li

class ManualInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.source=self.root/'source';self.source.mkdir();(self.source/'SKILL.md').write_text('name: fixture\n',encoding='utf-8');self.dest=self.root/'中文 space/fixture'
    def tearDown(self):self.tmp.cleanup()
    def seal(self):return li.seal(self.source,skill='fixture',source={'commit':'a'*40,'dirty':False})
    def test_initial_replace_backup_and_idempotence(self):
        self.seal();a=li.install_tree(self.source,self.dest);self.assertEqual(a['status'],'installed');before=(self.dest/'SKILL.md').read_bytes()
        with self.assertRaisesRegex(ValueError,'replace'):li.install_tree(self.source,self.dest)
        self.assertEqual(li.install_tree(self.source,self.dest,replace=True)['status'],'unchanged')
        (self.source/'SKILL.md').write_text('new bytes',encoding='utf-8');self.seal();b=li.install_tree(self.source,self.dest,replace=True)
        self.assertEqual((Path(b['previous_installation_backup'])/'SKILL.md').read_bytes(),before);self.assertTrue(b['host_reload_required'])
    def test_tamper_input_does_not_touch_old_install(self):
        self.seal();li.install_tree(self.source,self.dest);old=(self.dest/'SKILL.md').read_bytes();(self.source/'SKILL.md').write_text('tamper')
        with self.assertRaisesRegex(ValueError,'mismatch'):li.install_tree(self.source,self.dest,replace=True)
        self.assertEqual((self.dest/'SKILL.md').read_bytes(),old)
    def test_metadata_and_pool_binding(self):
        self.seal();p=self.source/li.IDENTITY;data=json.loads(p.read_text());data['source']['commit']='b'*40;p.write_text(json.dumps(data))
        self.assertRaisesRegex(ValueError,'metadata',li.verify,self.source)
        (self.source/'references').mkdir();(self.source/'references/manifest.json').write_text('{"version":"actual"}')
        self.assertRaisesRegex(ValueError,'pool',li.seal,self.source,skill='fixture',source={},pool={'version':'wrong'})
    def test_no_overwrite_unrelated_or_overlapping_directory(self):
        self.seal();self.dest.mkdir(parents=True);(self.dest/'keep').write_text('keep')
        self.assertRaisesRegex(ValueError,'not a Skill',li.install_tree,self.source,self.dest,replace=True)
        self.assertRaisesRegex(ValueError,'overlap',li.install_tree,self.source,self.source/'child')
    def test_lock_and_symlink_fail_closed(self):
        self.seal();self.dest.parent.mkdir(parents=True);lock=self.dest.with_name('.fixture.install-lock');lock.mkdir()
        self.assertRaisesRegex(ValueError,'lock',li.install_tree,self.source,self.dest);lock.rmdir()
        if hasattr(Path,'symlink_to'):
            link=self.root/'link'
            try: link.symlink_to(self.source,target_is_directory=True)
            except OSError as exc:
                if getattr(exc, 'winerror', None) == 1314: return  # No symlink privilege; junction test still runs.
                raise
            self.assertRaisesRegex(ValueError,'symlink',li.install_tree,link,self.dest)
    def test_failed_activation_restores_previous_bytes(self):
        self.seal();li.install_tree(self.source,self.dest);old=(self.dest/'SKILL.md').read_bytes()
        (self.source/'SKILL.md').write_text('update');self.seal();original=Path.rename
        def fail_stage(p,target):
            if '.stage-' in p.name:raise OSError('injected activation failure')
            return original(p,target)
        with patch.object(Path,'rename',fail_stage),self.assertRaises(OSError):li.install_tree(self.source,self.dest,replace=True)
        self.assertEqual((self.dest/'SKILL.md').read_bytes(),old);self.assertFalse(self.dest.with_name('.fixture.install-lock').exists())
    def test_secrets_and_symlinks_rejected(self):
        (self.source/'.env').write_text('secret');self.assertRaisesRegex(ValueError,'credential',self.seal)
    def test_describe_keeps_member_identity_but_not_latest_or_approval(self):
        (self.source/'references').mkdir();pool={'version':'trial','channel':'development'};(self.source/'references/manifest.json').write_text(json.dumps(pool));(self.source/'references/pool-members.json').write_text('{"members":[]}')
        li.seal(self.source,skill='fixture',source={'commit':'a'*40},pool=pool);d=li.describe(self.source)
        self.assertEqual(d['remote_freshness'],'not_checked');self.assertFalse(d['actual_host_skill_read_verified']);self.assertEqual(d['review_pool'],pool)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows junction contract')
    def test_windows_junction_source_and_parent_rejected(self):
        import subprocess
        self.seal()
        link=self.root/'junction'
        subprocess.run(['cmd','/c','mklink','/J',str(link),str(self.source)],check=True,capture_output=True)
        try:
            self.assertRaisesRegex(ValueError,'symlink',li.install_tree,link,self.dest)
            self.assertRaisesRegex(ValueError,'symlink',li.install_tree,self.source,link/'destination')
            self.assertRaisesRegex(ValueError,'real directory',li.verify,link)
        finally:
            link.rmdir()  # Remove junction only; target retained.

if __name__=='__main__':unittest.main()
