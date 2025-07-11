using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using ModularWebAPI.Shared.Enums;

namespace ModularWebAPI.Auth.Do
{
    public class Commande
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        [StringLength(50)]
        public string NumeroCommande { get; set; } = string.Empty;
        
        [Required]
        public Guid FournisseurId { get; set; }
        
        [Required]
        public CommandeStatus Status { get; set; } = CommandeStatus.Brouillon;
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal TotalHt { get; set; } = 0;
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal TotalTtc { get; set; } = 0;
        
        [Required]
        [Column(TypeName = "decimal(5,2)")]
        public decimal TauxTva { get; set; } = 20;
        
        public DateTime? DateCommande { get; set; }
        
        public DateTime? DateLivraisonPrevue { get; set; }
        
        public DateTime? DateLivraisonReelle { get; set; }
        
        public DateTime? DateProduction { get; set; }
        
        public DateTime? DateMiseDisposition { get; set; }
        
        public DateTime? DateEmbarquementCible { get; set; }
        
        [StringLength(1000)]
        public string? Notes { get; set; }
        
        [Required]
        public Guid CreatedBy { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        
        public ICollection<LigneCommande> Lignes { get; set; } = new List<LigneCommande>();
    }
}