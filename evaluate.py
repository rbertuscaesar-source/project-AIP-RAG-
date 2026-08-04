"""
RAG Evaluation Script
Mengukur akurasi sistem RAG menggunakan golden test set 49 Q&A pairs
Metrik: Answer Accuracy, Keyword Match Rate, Response Time
"""

import json
import time
import requests
from datetime import datetime

# ============================================
# GOLDEN TEST SET — 49 Q&A PAIRS
# ============================================
GOLDEN_QA = [
    # SOP 001 — Pendaftaran Mahasiswa Baru
    {"q": "Apa tujuan dari SOP Pendaftaran Mahasiswa Baru?", "keywords": ["pendaftaran", "sistematis", "tertib", "transparan"]},
    {"q": "Jalur apa saja yang tersedia untuk pendaftaran mahasiswa baru?", "keywords": ["SNBP", "SNBT", "Mandiri"]},
    {"q": "Apa yang dimaksud dengan NIM?", "keywords": ["Nomor Induk Mahasiswa", "Biro Administrasi Akademik"]},
    {"q": "Bagaimana prosedur pengisian formulir pendaftaran mahasiswa baru?", "keywords": ["online", "portal", "pmb.universitasnusantara"]},
    {"q": "Berapa lama batas waktu pembayaran UKT setelah pengisian formulir?", "keywords": ["3x24 jam", "bank"]},
    {"q": "Dokumen apa saja yang harus diserahkan saat pengumpulan berkas pendaftaran?", "keywords": ["ijazah", "KTP", "pas foto", "pembayaran"]},
    {"q": "Berapa lama proses verifikasi berkas pendaftaran mahasiswa baru?", "keywords": ["2 hari kerja"]},
    {"q": "Berapa lama NIM dan KTM diterbitkan setelah verifikasi berkas selesai?", "keywords": ["3 hari kerja"]},
    {"q": "Apa konsekuensi jika calon mahasiswa tidak menyelesaikan pendaftaran ulang tepat waktu?", "keywords": ["mengundurkan diri", "cadangan"]},
    {"q": "Apakah orientasi mahasiswa baru wajib diikuti?", "keywords": ["wajib", "OMBA", "pembatalan"]},

    # SOP 002 — Tugas Akhir
    {"q": "Apa syarat untuk mengajukan judul tugas akhir atau skripsi?", "keywords": ["120 SKS", "IPK", "2.50", "Metodologi Penelitian"]},
    {"q": "Bagaimana prosedur pengajuan judul tugas akhir?", "keywords": ["Dosen Wali", "Form TA-01", "Koordinator"]},
    {"q": "Berapa banyak bimbingan minimum dengan dosen pembimbing utama?", "keywords": ["8 kali", "DPU"]},
    {"q": "Berapa maksimal mahasiswa yang bisa dibimbing satu dosen per semester?", "keywords": ["8 mahasiswa"]},
    {"q": "Apa yang harus diserahkan saat mendaftar sidang tugas akhir?", "keywords": ["4 eksemplar", "Form TA-04", "Kartu Bimbingan"]},
    {"q": "Apa sanksi jika mahasiswa tidak menyelesaikan tugas akhir dalam 2 semester?", "keywords": ["pendaftaran ulang", "evaluasi akademik"]},
    {"q": "Berapa lama proses evaluasi judul tugas akhir oleh Koordinator TA?", "keywords": ["7 hari kerja"]},
    {"q": "Di mana formulir pengajuan judul tugas akhir dapat diperoleh?", "keywords": ["Sekretariat", "akademik.universitasnusantara"]},

    # SOP 003 — Peminjaman Ruang
    {"q": "Apa tujuan SOP Peminjaman Ruang dan Fasilitas Kampus?", "keywords": ["peminjaman", "ruang kuliah", "aula", "laboratorium"]},
    {"q": "Berapa kapasitas aula utama di Universitas Nusantara Teknologi?", "keywords": ["500 orang"]},
    {"q": "Berapa jauh hari sebelumnya harus mengajukan peminjaman ruang?", "keywords": ["3 hari kerja", "SIMFAS"]},
    {"q": "Siapa yang harus memberikan persetujuan untuk kegiatan berskala besar?", "keywords": ["Wakil Rektor II", "100 orang"]},
    {"q": "Bagaimana cara mengambil kunci ruangan setelah peminjaman disetujui?", "keywords": ["Pos Satpam", "Surat Izin", "KTM", "30 menit"]},
    {"q": "Apa yang dilarang selama menggunakan fasilitas kampus?", "keywords": ["memindahkan perabot", "makanan", "merokok"]},
    {"q": "Apa yang terjadi jika ada kerusakan fasilitas kampus selama peminjaman?", "keywords": ["Berita Acara", "tanggung jawab"]},

    # SOP 004 — Cuti Akademik
    {"q": "Apa ketentuan umum untuk mengajukan cuti akademik?", "keywords": ["2 semester aktif", "maksimal", "kumulatif"]},
    {"q": "Apa saja alasan yang dapat diterima untuk pengajuan cuti akademik?", "keywords": ["Kesehatan", "Keluarga", "Ekonomi", "rawat inap"]},
    {"q": "Bagaimana prosedur pengajuan cuti akademik?", "keywords": ["Dosen Wali", "Form CUTI-01", "Ketua Program Studi", "Wakil Rektor"]},
    {"q": "Berapa lama proses persetujuan cuti akademik oleh Ketua Program Studi?", "keywords": ["3 hari kerja"]},
    {"q": "Bagaimana cara aktivasi kembali setelah cuti akademik?", "keywords": ["reaktivasi", "2 minggu", "Biro Administrasi Akademik"]},
    {"q": "Apakah mahasiswa cuti akademik tetap dikenakan biaya UKT?", "keywords": ["tidak", "UKT"]},
    {"q": "Berapa maksimal cuti akademik yang bisa diambil selama masa studi?", "keywords": ["2 semester", "kumulatif"]},
    {"q": "Apakah masa cuti akademik dihitung sebagai masa studi?", "keywords": ["tidak dihitung", "masa studi aktif", "batas waktu"]},

    # SOP 005 — Laboratorium Komputer
    {"q": "Apa tata tertib yang harus dipatuhi saat menggunakan laboratorium komputer?", "keywords": ["KTM", "buku tamu", "sandal anti-statis", "dilarang"]},
    {"q": "Sampai jam berapa laboratorium komputer buka pada hari kerja?", "keywords": ["21.00", "WIB"]},
    {"q": "Bagaimana cara memesan slot waktu untuk menggunakan laboratorium komputer?", "keywords": ["SML", "Petugas Laboratorium", "7 hari", "1 hari"]},
    {"q": "Di mana data dan file harus disimpan saat menggunakan laboratorium komputer?", "keywords": ["Google Drive", "cloud", "tidak lokal"]},
    {"q": "Bagaimana cara login di laboratorium komputer?", "keywords": ["SSO", "username", "password", "audit log"]},
    {"q": "Apa yang harus dilakukan sebelum meninggalkan laboratorium komputer?", "keywords": ["logout", "monitor", "laboran"]},
    {"q": "Berapa kapasitas laboratorium komputer di Universitas Nusantara Teknologi?", "keywords": ["30 orang"]},
    {"q": "Apakah satu pengguna boleh menggunakan lebih dari satu komputer di laboratorium?", "keywords": ["1 unit", "Kepala Laboratorium"]},

    # Cross-topic
    {"q": "Dimana lokasi pengumpulan berkas pendaftaran mahasiswa baru?", "keywords": ["Gedung Rektorat", "Loket PMB", "lantai 1"]},
    {"q": "Apa yang dimaksud dengan Panitia PMB?", "keywords": ["tim", "Rektor", "Penerimaan Mahasiswa Baru"]},
    {"q": "Bagaimana cara mendapatkan Surat Izin Penggunaan fasilitas kampus?", "keywords": ["SIMFAS", "otomatis", "diunduh"]},
    {"q": "Siapa yang mengesahkan cuti akademik secara final?", "keywords": ["Wakil Rektor I", "5 hari kerja"]},
    {"q": "Melalui sistem apa peminjaman fasilitas kampus diajukan?", "keywords": ["SIMFAS", "fasilitas.universitasnusantara"]},
    {"q": "Apa yang dimaksud dengan Form TA-01?", "keywords": ["Formulir Pengajuan Judul", "3 pilihan", "latar belakang"]},
    {"q": "Sampai jam berapa laboratorium komputer buka pada hari Sabtu?", "keywords": ["16.00", "Sabtu"]},
]

# ============================================
# EVALUASI
# ============================================
API_URL = "http://localhost:8000/api/chat"

def evaluate():
    print("=" * 60)
    print("RAG EVALUATION — Enterprise SOP Assistant")
    print(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total pertanyaan: {len(GOLDEN_QA)}")
    print("=" * 60)

    results = []
    total_time = 0
    correct = 0
    partial = 0
    failed = 0

    for i, qa in enumerate(GOLDEN_QA, 1):
        question = qa["q"]
        keywords = qa["keywords"]

        print(f"\n[{i:02d}/{len(GOLDEN_QA)}] {question[:60]}...")

        start = time.time()
        try:
            response = requests.post(
                API_URL,
                json={"question": question},
                timeout=30
            )
            elapsed = time.time() - start
            total_time += elapsed

            if response.status_code == 200:
                answer = response.json().get("answer", "").lower()

                # Cek keyword matches
                matched = [kw for kw in keywords if kw.lower() in answer]
                match_rate = len(matched) / len(keywords)

                if match_rate >= 0.6:
                    status = "✅ CORRECT"
                    correct += 1
                elif match_rate >= 0.3:
                    status = "⚠️  PARTIAL"
                    partial += 1
                else:
                    status = "❌ WRONG"
                    failed += 1

                print(f"   Status : {status} ({len(matched)}/{len(keywords)} keywords matched)")
                print(f"   Time   : {elapsed:.2f}s")

                results.append({
                    "question": question,
                    "keywords": keywords,
                    "matched": matched,
                    "match_rate": round(match_rate, 2),
                    "status": status.strip(),
                    "response_time": round(elapsed, 2),
                    "answer_preview": answer[:200]
                })
            else:
                print(f"   Status : ❌ HTTP {response.status_code}")
                failed += 1
                results.append({
                    "question": question,
                    "status": f"HTTP {response.status_code}",
                    "match_rate": 0,
                    "response_time": 0
                })

        except Exception as e:
            elapsed = time.time() - start
            print(f"   Status : ❌ ERROR — {str(e)[:50]}")
            failed += 1
            results.append({
                "question": question,
                "status": f"ERROR: {str(e)[:50]}",
                "match_rate": 0,
                "response_time": round(elapsed, 2)
            })

        # Jeda kecil agar tidak kena rate limit
        time.sleep(1.5)

    # ============================================
    # SUMMARY
    # ============================================
    total = len(GOLDEN_QA)
    accuracy = (correct + partial * 0.5) / total * 100
    avg_time = total_time / total if total > 0 else 0

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Questions  : {total}")
    print(f"✅ Correct       : {correct} ({correct/total*100:.1f}%)")
    print(f"⚠️  Partial       : {partial} ({partial/total*100:.1f}%)")
    print(f"❌ Wrong/Error   : {failed} ({failed/total*100:.1f}%)")
    print(f"📊 Accuracy Score: {accuracy:.1f}%")
    print(f"⏱️  Avg Response  : {avg_time:.2f}s")
    print("=" * 60)

    # Simpan hasil ke JSON
    output = {
        "metadata": {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_questions": total,
            "model": "gemini-2.5-flash",
            "embedding": "gemini-embedding-001"
        },
        "summary": {
            "correct": correct,
            "partial": partial,
            "wrong": failed,
            "accuracy_score": round(accuracy, 1),
            "avg_response_time": round(avg_time, 2)
        },
        "results": results
    }

    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Hasil disimpan ke: evaluation_results.json")
    print(f"\n📋 Untuk PPT/laporan:")
    print(f"   - Answer Accuracy : {accuracy:.1f}%")
    print(f"   - Correct         : {correct}/{total}")
    print(f"   - Partial Match   : {partial}/{total}")
    print(f"   - Avg Response    : {avg_time:.2f}s")

if __name__ == "__main__":
    evaluate()
