from src.data_loader.featurizer.utils.load import load
from src.data_loader.featurizer.utils.fbank import Fbank
from src.data_loader.featurizer.utils.normalize import normalization
from src.data_loader.featurizer.utils.sub_sample import concat_and_subsample
from src.data_loader.featurizer.utils.speed_perturb import speed_perturb
from src.utils.vocab import Vocab
import torch as t

class Featurizer:
    def __init__(self, n_mel=80, left_frames=3, right_frames=0, skip_frames=2, vocab_path=None, speed_perturb=False):
        super(Featurizer, self).__init__()
        self.fbank = Fbank(sample_rate=16000, n_fft=512, win_length=400, hop_length=160, n_mels=n_mel)
        if not vocab_path is None:
            self.vocab = Vocab(vocab_path)
        else:
            self.vocab = None
        self.speed_perturb = speed_perturb

    @property
    def unk_id(self):
        return self.vocab.unk_id

    def __call__(self, file, target=None):
        sig = load(file, do_vad=True)
        if self.speed_perturb:
            sig = speed_perturb(sig, 80, 120, 4)
        feature = self.fbank(sig)
        feature = normalization(feature)
        feature = concat_and_subsample(feature.numpy(), left_frames=4, skip_frames=3)
        feature_length = len(feature)
        if not self.vocab is None:
            target_id = self.vocab.str2id(target)
            target_length = len(target_id)
        else:
            target_id = None
            target_length = None
        return t.from_numpy(feature), feature_length, t.LongTensor(target_id), target_length


