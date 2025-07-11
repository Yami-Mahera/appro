using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ModularWebAPI.Auth.Do
{
    public class CalculCouverture
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        public Guid ArticleId { get; set; }
        
        [Required]
        public DateTime DateCalcul { get; set; } = DateTime.UtcNow;
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal Cms { get; set; } // Consommation Moyenne Semaine
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal Cmc { get; set; } // Consommation Moyenne Cumul
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal Qm { get; set; } // Quantité Minimum
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal Cr { get; set; } // Couverture Réelle
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal CouvertureActuelle { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}