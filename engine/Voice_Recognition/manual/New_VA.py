from speechbrain.pretrained import SpeakerRecognition

# Load Pre-trained ECAPA-TDNN Model
model = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)
