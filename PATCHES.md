# Patches applied to the code for this bundle

Only absolute local paths and operations comments were changed (paths now resolve relative to each script; the METR input directory is `data/metr/`, overridable with `FDATA`). No statistic, seed or estimator was edited.
Some of these files were pinned by SHA-256 before the runs (`real_data/PINS.txt`, `results/code_sha256.txt`, `topj/SCRIPTS_SHA256.txt`, `multibench_audit/results/audit_pins.txt`). Those pins name the *original* files; the original and bundle hashes of every patched file are below, so a reader can confirm that the diff is only the path/comment lines.

| file | sha256 original | sha256 in this bundle |
|---|---|---|
| `code/analyze_size.py` | `669021f66ce321cd93893a4d23826f9aa85630baf60966130a7ad5ad34d635fc` | `e7c46cd03128f7fefc6c4eff05c5ce806ba9e9529951f50627d599fa843b6db4` |
| `code/split_task.py` | `f8f5d99ba2d4d0f80efc4182f7c539b812e0782673307fc2ec68790cc09e1460` | `19f11981e40a450a6ac8774dd44c1b749c85cd3422e34b8cff1b9a1ee406b13b` |
| `code/analyze_power_null.py` | `b2d87c38136c455fea56bb644276183df47b5afb9ead8bff0962de8c544cfe74` | `5ce2012c623c47ec8f24feffbdf62d225df48c0ae175f17d6bf35fefc71cb2a3` |
| `code/fcore.py` | `45cf8a069a3b7c3dff9f13aa003af3b43044f475a2af7a8eb39e43049e8ee12d` | `e40f92c601edfccf812c39b639f00652d064934907e94bc2c381856fd5ea51e8` |
| `code/hinge_study.py` | `c15276368f174a2d7a8209eb5e2345714c5366202dd568157e2b6bf5fe04586f` | `ea74ffb25cb29030172752fc1dea24093a56fba8d8c6d621db83adf121e6fdd1` |
| `code/holdout.py` | `356fecf33ad1cc2d3ed26ce2a3118eeafe4e2a1529833fb7b2266b7bc4ce96da` | `e1ec4e0b4b2dfe302fa89ea125847385c2e0b9059a5c10f6fcc6b78ab86bacd8` |
| `code/size_sim.py` | `e1dd6c2a1be08f41f6bb1ab63a2f22fc85882878ee0d5134533ae8e23e66403d` | `44a41e41c6ef1dae1dd3d252d6d0528d8de4116b06f8672130c2b7b2895c684a` |
| `code/vuong.py` | `1f7ed26407df023d90d63a0bcfdb1131743fd3cfaf017459bffbbb504ab6a4e2` | `913fb4f310792528888e7b10116d4cf8251b205ca164b9c5337b850cbd9aba05` |
| `code/calibrate.py` | `6c094c2445d166f86e36054a85a453f200c550407e29ec8d05b8d286e79f055a` | `9d8e7ed25da6f9f62af61c74bc5a105a32aa8a7d28a7b1859080bc756984f912` |
| `code/real_run.py` | `26ec25b59ed491e7dd9fc6d1707c2f873336092c7d4019747cfabf56b26884c7` | `67f8b6b2083510c84c6c6bd711f0f12496d12ae9f7b19809c03f1fb075349e1e` |
| `code/validate_fit.py` | `02f8d0ced83543d0400610c0dcbc8a472ffd0ce988c9a3f6d0c28b7df9b20923` | `01bd81a5469012d21a62c3e4946f4bb257b4026150fa0c9b12e49f8a0eb8f2b6` |
| `code/analyze_power.py` | `125852ac84a3463f2b26a5ec28c14cba6766aed3193b207199f6f0a843f03dd7` | `b176e87f2d976a98cbb60d5bfd5a9f186f2aa65d63643bcd651a8ef4c9c84c58` |
| `code/power_sim.py` | `30719f3a2b33917cb079ffa79d3a13048e47662dfd5f2248364cb0d73936b4fa` | `46c8906ac5cdee914801028c8c7fc0034069090e01da180ee9bdaaee73bcdde4` |
| `design/audit_adjustment.py` | `dd6122a6b2c12c68f4a9f8c7cd8fe7309de933e3345edeff431bd35d9052e873` | `ed87e4f5ad6fbd80cd73714a8dfc09ec55bcc71d78c248bbfbdb77b1925fbcdb` |
| `design/fcore.py` | `45cf8a069a3b7c3dff9f13aa003af3b43044f475a2af7a8eb39e43049e8ee12d` | `e40f92c601edfccf812c39b639f00652d064934907e94bc2c381856fd5ea51e8` |
| `design/grid_a2.py` | `e38c7ac604a6b6bdfaa56f9cb5b9be2d3905be4ef02d311da9ac67c3900a8f32` | `ccefd768d70cc9880dca05d257067129d21b46fdd02314928ef5c647dea90203` |
| `design/grid_fu1.py` | `40b2cb9d51e73a1284cc32da65f1c44705cf0afa30cfdac57346a42e31f960ac` | `456d97f990d02e4afbda5afa198c4e1c298aae4fc7f4884a8f6c241e6b11adcd` |
| `real_data/real_data_run.py` | `c8025904a2ba31bb03f5189ab8167a60ec03fe14fef2b58e88ee6f342a539d55` | `4ab0397c010d1d43ad0dcce2474710ecb1c4c4262f16bc559adbf3e4e7d1d1ae` |
| `multibench_audit/audit_core.py` | `f6b123ee344ef4cb8586008ef074cb4669d98b0a3e6875526f630b1f8548c8e2` | `1b757afb4c8bc6955075c8b09f3779fa1b3d029bda8dc076d923365b239a772d` |
| `topj/topj_common.py` | `4b79b965d9eee73ea4c1527464019bc392478d6f9306b08a49ad2c5e30869715` | `bbfa1f5a03d3f359a092624ed6253ed2c1578c870bdd37824541be4c84b0e1da` |
| `redteam_final/run_abcf.py` | `83f9c3fbbaf5a0664859167b5be1ab39d02914d10ed7ac60a3d2a32c9a4f4e08` | `59340b2f09dd35d63c1d65941d5885245467397c031fcb84dfb2f426b52a2bf0` |
| `redteam_final/run_d.py` | `084a03772888ad2d9199f171351fe970d479a678f8b1745442164d2caeb400d3` | `1ac3534018ca61833b263b3220e4d28590546359d253e9bf989aa239fd0a2665` |
| `U_frontier_trend_forecast_coverage/code/ucore.py` | `981c001d0637f800de86ef9dee58e1f9aa3a93b0d8d993142684b50d101de37a` | `f64589890ad05090bb6eb6bacbe58484b3ac0c00027e9ea1dabf602493a4bdee` |
| `paper/make_sensitivity.py` | `1405ad5b5c0418dfd7c0d12c3e8870ce5b34c9f9dd04d5ce047e7f60a0f81f9e` | `de83e36f5ba504c50c0765588df0df0874fe808f2af850f8b6874e1cf55582e8` |
| `paper/make_numbers.py` | `544a2e8daa9c95e2e9173ab0f1011ec0c3a96981fbb23f1c8fc305bf674a094f` | `da2857cbf33cf1c45f6136195076deed649dc83188321864d2cf191892ac50cf` |

Line-level redactions of internal operations notes in the narrative files (`*.md`, logs) are recorded in `REDACTIONS.md`.
