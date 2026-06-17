# Déploiement — LinguaScope

LinguaScope a deux remotes :

| Remote | URL | Contenu |
|---|---|---|
| `origin` | github.com/chniang/linguascope | code + images (historique complet) |
| `hf` | huggingface.co/spaces/TIJAANI/linguascope | code texte uniquement (HF refuse les binaires) |

---

## Workflow normal

```bash
git push origin main        # toujours en premier
bash scripts/push-hf.sh     # sync HF ensuite
```

`git push origin main` est un push classique, sans restriction.  
`push-hf.sh` est nécessaire car HF rejette les commits contenant des binaires (PNG, etc.) — les images du README sont hébergées sur GitHub raw et référencées par URL absolue.

---

## Ce que fait `push-hf.sh`

1. Fetch `hf/main` pour connaître l'état actuel du Space
2. Diff `hf/main..main`, filtre les extensions binaires (`*.png`, `*.jpg`, `*.gif`, `*.pdf`, `*.woff`…)
3. Crée une branche `hf-deploy` depuis le tip HF (historique parallèle, sans binaires)
4. Applique les fichiers texte modifiés/ajoutés/supprimés depuis le dernier sync
5. Commit + push `hf-deploy → hf/main`, supprime la branche locale

Si HF est déjà à jour (aucun fichier texte modifié), le script sort sans rien faire.

---

## Quand l'utiliser

| Changement | `origin` | `push-hf.sh` |
|---|---|---|
| Code Python (`app.py`, `src/`) | ✅ | ✅ obligatoire pour que l'app redémarre |
| README / DEPLOY.md | ✅ | ✅ pour mettre à jour la fiche du Space |
| Ajout d'images dans `screenshots/` | ✅ | ✗ inutile (images sur GitHub raw) |
| `.gitignore`, `requirements.txt` | ✅ | ✅ |

---

## Ajouter un nouveau type de fichier binaire à exclure

Editer la variable `BINARY_EXT` dans `scripts/push-hf.sh` :

```bash
BINARY_EXT='\.(png|jpg|jpeg|gif|webp|ico|pdf|zip|tar\.gz|woff2?|ttf|eot)$'
```

---

## Première utilisation sur un nouveau poste

```bash
git clone https://github.com/chniang/linguascope.git
cd linguascope
git remote add hf https://huggingface.co/spaces/TIJAANI/linguascope
git fetch hf
```

Ensuite le workflow normal s'applique.
