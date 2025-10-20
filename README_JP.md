# Python ��ʃL���v�`���������c�[��  
[English version �� README.md](./README.md)

## �T�v
���̃v���W�F�N�g�́A**�L�[�{�[�h����ŉ�ʂ�؂�ւ�����C�ӂ̃A�v���P�[�V����**����A�A���I�ɉ�ʓ��e�������L���v�`�����邽�߂� Python �c�[���ł��B  
�擾�����摜�� **1��PDF** �܂��� **�͂��Ƃ̕���PDF** �ɂ܂Ƃ߂邱�Ƃ��ł��܂��B

�{�c�[���͈ȉ���2�̃X�N���v�g�ō\������Ă��܂��B
- **capture.py** ? �y�[�W���Ƃɉ�ʂ������L���v�`�����܂��B
- **merge.py** ? �L���v�`�������摜���g���~���O���APDF�Ƃ��Č������܂��B

---

## ����
- �ݒ肵���z�b�g�L�[�ŉ�ʂ������L���v�`���B
- �ǂݍ��ݒx����g���~���O�͈͂��_��ɐݒ�\�B
- �o�͉摜���͂��ƁA�܂��͑S�̂��܂Ƃ߂�PDF���B
- �g���~���O�E�����EPDF�������̐i�s�󋵃o�[��\���\�B
- **uv** �ɂ�� Python �p�b�P�[�W�Ǘ����̗p�B

---

## �Z�b�g�A�b�v

### 1. [uv](https://github.com/astral-sh/uv) �̃C���X�g�[��
���̃v���W�F�N�g�ł� Python �̈ˑ��֌W�Ǘ��� `uv` ���g�p���Ă��܂��B

```bash
pip install uv
```

### 2. �ˑ��p�b�P�[�W�̃C���X�g�[��
�v���W�F�N�g�f�B���N�g���ňȉ������s���܂��B
```bash
uv sync
```
����ɂ��A���z�����쐬����A`pyproject.toml` �ɋL�ڂ��ꂽ�K�v�ȃ��C�u�����������I�ɃC���X�g�[������܂��B
```
img2pdf, pillow, pyautogui, pygetwindow, pypdf, tqdm
```

---

## �g����

### 1. �摜�L���v�`��
**capture.py** �̐ݒ��ҏW���A�L���v�`���Ώۂ̃E�B���h�E�^�C�g����z�b�g�L�[���w�肵�܂��B

���s�R�}���h:
```bash
uv run capture.py
```

���̃X�N���v�g�͈ȉ������s���܂�:
- �w�肵���E�B���h�E���A�N�e�B�u���i�\�ȏꍇ�j
- ���L�[�܂���PageDown�L�[�Ńy�[�W��؂�ւ�
- �e�y�[�W�̃X�N���[���V���b�g�� `outputs/` �t�H���_�ɕۑ�

���s���� `Ctrl + C` �ň��S�ɒ�~�ł��܂��B

---

### 2. PDF�ւ̌���
�S�y�[�W�̃L���v�`��������A**merge.py** �̐ݒ�Ńy�[�W�͈͂�g���~���O�ݒ���w�肵�܂��B

���s�R�}���h:
```bash
uv run merge.py
```

���̃X�N���v�g�͈ȉ������s���܂�:
- �摜���g���~���O�i�L�����j
- �͈͂��Ƃ̏�PDF���쐬�i�C�Ӂj
- �S�y�[�W���܂Ƃ߂��ŏIPDF�� `pdf_out/` �ɏo��

---

## �f�B���N�g���\��
```
python-ebook-capturer/
��
������ capture.py           # ��ʃL���v�`���������X�N���v�g
������ merge.py             # PDF�����E�g���~���O�X�N���v�g
������ pyproject.toml       # �v���W�F�N�g�ݒ�ƈˑ��֌W
������ outputs/             # �L���v�`���摜�̕ۑ���i���������j
������ pdf_out/             # PDF�o�̓t�H���_�i���������j
```

---

## ���ӎ���
- ���L�[�Ńy�[�W���肪�\�ȃA�v���P�[�V�����ł���Η��p�ł��܂��B
- `capture.py` �� `delay_after_flip` �𒲐����邱�ƂŁA��ʂ̓ǂݍ��݊�����҂��Ă���L���v�`���\�ł��B
- �ꎞ�I�ɐ��������g���~���O�ς݉摜�́A����������Ɏ����폜����܂��B
