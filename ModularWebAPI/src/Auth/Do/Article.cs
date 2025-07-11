using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ModularWebAPI.Auth.Do
{
    public class Article
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        [StringLength(50)]
        public string Reference { get; set; } = string.Empty;
        
        [Required]
        [StringLength(200)]
        public string Nom { get; set; } = string.Empty;
        
        [StringLength(1000)]
        public string? Description { get; set; }
        
        [StringLength(100)]
        public string? Famille { get; set; }
        
        [Required]
        public Guid FournisseurId { get; set; }
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal PrixUnitaire { get; set; }
        
        [Required]
        [StringLength(20)]
        public string Unite { get; set; } = string.Empty;
        
        public int SeuilMin { get; set; } = 0;
        
        public int SeuilMax { get; set; } = 0;
        
        public int StockActuel { get; set; } = 0;
        
        public int? DureeVie { get; set; }
        
        [StringLength(200)]
        public string? EmplacementStockage { get; set; }
        
        public bool Active { get; set; } = true;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }
}