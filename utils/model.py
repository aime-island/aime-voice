import os
from deepspeech import Model


class DeepSpeech(Model):
    
    def __init__(self, config, lm):

        # Config
        self.config = config
        self.path = self.config.get('path')
        self.modelcfg = self.config.get('model')
        self.model = os.path.join(self.path,'output_graph.pbmm')
        self.alphabet = os.path.join(self.path, 'alphabet.txt')
        self.beam_width = self.modelcfg.get('beam_width')
        self.n_features = self.modelcfg.get('n_features')
        self.n_context = self.modelcfg.get('n_context')
        self.lmcfg = self.config.get('lm')

        # Initialize DS model
        super().__init__(
            self.model, 
            self.n_features, 
            self.n_context, 
            self.alphabet, 
            self.beam_width)
        
        self.enable_lm(lm)


    def enable_lm(self, lm):
        self.lm = self.lmcfg.get(lm)
        self.lm_path = os.path.join(self.path, self.lm.get('path'))
        self.lmbin = os.path.join(self.lm_path, 'lm.binary')
        self.trie = os.path.join(self.lm_path, 'trie')
        self.lm_weight = self.lm.get('lm_weight')
        self.w_weight = self.lm.get('w_weight')

        self.enableDecoderWithLM(
            self.alphabet,
            self.lmbin,
            self.trie,
            self.lm_weight,
            self.w_weight
        )