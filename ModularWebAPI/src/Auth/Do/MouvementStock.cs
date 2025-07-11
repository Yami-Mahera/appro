using System.ComponentModel.DataAnnotations;
using ModularWebAPI.Shared.Enums;

namespace ModularWebAPI.Auth.Do
{
    public class MouvementStock
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        public Guid ArticleId { get; set; }
        
        [Required]
        public TypeMouvement TypeMouvement { get; set; }
        
        [Required]
        public int Quantite { get; set; }
        
        [Required]
        public int StockAvant { get; set; }
        
        [Required]
        public int StockApres { get; set; }
        
        public DateTime DateMouvement { get; set; } = DateTime.UtcNow;
        
        public Guid? CommandeId { get; set; }
        
        [StringLength(100)]
        public string? ReferenceDocument { get; set; }
        
        [StringLength(500)]
        public string? Commentaire { get; set; }
        
        [Required]
        public Guid CreatedBy { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}